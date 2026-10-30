"""Attaque par dictionnaire — couvre TOUT le cas 1 et TOUT le cas 2,
plus un large éventail de mots familiers pour le cas 3."""
import itertools
import time

from .crypto import fingerprint_bytes
from .charsets import BINARY, DIGITS_1_4


def _all(charset, length):
    return ["".join(p) for p in itertools.product(charset, repeat=length)]


# Espaces COMPLETS exigés par l'énoncé
CASE1_WORDS = _all(BINARY, 3)        # 8 mots
CASE2_WORDS = _all(DIGITS_1_4, 4)    # 256 mots


# Mots familiers (cas 3) : les 100 premiers de rockyou + français + prénoms
FAMILIAR_WORDS = [
    # top rockyou
    "password", "123456", "123456789", "12345678", "12345", "qwerty",
    "abc123", "football", "monkey", "letmein", "shadow", "master",
    "sunshine", "princess", "superman", "batman", "trustno1", "iloveyou",
    "welcome", "admin", "root", "toor", "guest", "test", "hello",
    # français / contexte
    "bonjour", "salut", "bonsoir", "merci", "amour", "soleil", "lune",
    "fromage", "baguette", "croissant", "paris", "france", "algerie",
    "alger", "oran", "annaba", "usthb", "universite", "etudiant",
    "professeur", "vacances", "famille", "musique", "voiture", "maison",
    "travail", "secret", "ordinateur", "telephone", "internet",
    "facebook", "google", "youtube", "motdepasse",
    # prénoms
    "mohamed", "ahmed", "ali", "hassan", "youssef", "omar", "karim",
    "yacine", "amine", "bilal", "sofiane", "mehdi", "rayan", "adam",
    "nathan", "lucas", "hugo", "leo", "gabriel", "louis", "jules",
    "arthur", "sarah", "emma", "lea", "chloe", "manon", "camille",
    "julie", "laura", "ines", "lina", "yasmine", "amira", "nadia", "samia",
    # leet / variantes déjà connues
    "p@ssw0rd", "passw0rd", "pa$$word", "s3cr3t", "adm1n", "r00t",
    "l3tm3in", "qwerty123", "azerty123", "iloveyou1", "sunshine1",
    # clavier
    "qwertyuiop", "azertyuiop", "1q2w3e4r", "1qaz2wsx", "zaq12wsx",
]


def _generated_common():
    """Répétitions et séquences très fréquentes."""
    words = set()
    for c in "abcdefghijklmnopqrstuvwxyz0123456789":
        words.add(c * 3)
        words.add(c * 4)
    words.update([
        "abc", "abcd", "abcde", "abcdef", "123", "1234", "12345", "123456",
        "0000", "1111", "2222", "3333", "4444",
        "5555", "6666", "7777", "8888", "9999",
    ])
    return words


def _variants(base):
    """Casse + suffixes usuels (0-9, 1234, !, @, années…)."""
    forms = {base, base.lower(), base.upper(), base.capitalize()}
    suffixes = ["", "0", "1", "2", "3", "7", "9", "12", "123", "1234",
                "!", "@", "#", "!!", "!1", "@1",
                "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    return {f + s for f in forms for s in suffixes}


_WORDLIST_CACHE = None
_WORDSET_CACHE = None


def build_wordlist():
    global _WORDLIST_CACHE
    if _WORDLIST_CACHE is not None:
        return _WORDLIST_CACHE
    words, seen = [], set()

    def add(w):
        if w and w not in seen:
            seen.add(w)
            words.append(w)

    for w in CASE1_WORDS:          add(w)   # espace COMPLET cas 1
    for w in CASE2_WORDS:          add(w)   # espace COMPLET cas 2
    for w in FAMILIAR_WORDS:       add(w)   # mots familiers exacts
    for w in _generated_common():  add(w)   # répétitions / séquences
    for base in FAMILIAR_WORDS:              # variantes transformées
        for v in _variants(base):
            add(v)

    _WORDLIST_CACHE = words
    return words


def build_wordset():
    global _WORDSET_CACHE
    if _WORDSET_CACHE is None:
        _WORDSET_CACHE = set(build_wordlist())
    return _WORDSET_CACHE


def dictionary_attack(target_hash, wordlist=None):
    """Retourne (mot_trouvé_ou_None, nb_essais, secondes)."""
    words = wordlist if wordlist is not None else build_wordlist()
    target = bytes.fromhex(target_hash)
    start = time.perf_counter()
    for i, candidate in enumerate(words, 1):
        if fingerprint_bytes(candidate) == target:
            return candidate, i, time.perf_counter() - start
    return None, len(words), time.perf_counter() - start