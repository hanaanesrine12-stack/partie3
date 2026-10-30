"""Politique de robustesse + verrouillage des tentatives."""
import time

from .crypto import check_record
from .dictionary import build_wordset

KEYBOARD_WALKS = ("qwerty", "azerty", "qwertyuiop", "azertyuiop",
                  "1q2w3e4r", "1qaz2wsx", "zaq12wsx", "qsdfghjklm")
SYMBOLS = "+*-_!@#$%&()=?[]{};:,.<>"


def strength_problems(password):
    problems = []
    if len(password) < 12:
        problems.append("longueur inférieure à 12 caractères")
    if not any(c.islower() for c in password):
        problems.append("aucune minuscule")
    if not any(c.isupper() for c in password):
        problems.append("aucune majuscule")
    if not any(c.isdigit() for c in password):
        problems.append("aucun chiffre")
    if not any(c in SYMBOLS for c in password):
        problems.append("aucun symbole")
    if password in build_wordset():
        problems.append("présent dans la liste noire des mots de passe communs")
    low = password.lower()
    for walk in KEYBOARD_WALKS:
        if walk in low:
            problems.append("suite de clavier détectée (%s)" % walk)
            break
    if len(set(password)) < max(4, len(password) // 3):
        problems.append("trop peu de caractères distincts")
    return problems


class LoginGuard:
    """Verrouillage temporaire après N échecs — contre la force brute."""

    def __init__(self, record, max_attempts=5, lockout_seconds=30):
        self.record = record
        self.max_attempts = max_attempts
        self.lockout_seconds = lockout_seconds
        self.failures = 0
        self.locked_until = None

    def try_login(self, attempt, now=None):
        now = time.time() if now is None else now
        if self.locked_until is not None and now < self.locked_until:
            return "refusé (compte verrouillé)"
        if check_record(self.record, attempt):
            self.failures = 0
            self.locked_until = None
            return "accepté"
        self.failures += 1
        if self.failures >= self.max_attempts:
            self.locked_until = now + self.lockout_seconds
            self.failures = 0
            return "refusé (verrouillé pour %ds)" % self.lockout_seconds
        return "refusé (mot de passe incorrect, %d/%d)" % (
            self.failures, self.max_attempts)