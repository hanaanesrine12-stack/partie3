"""Façade de la partie 3 : c'est CE module qu'importe app.py."""
from .charsets import BINARY, DIGITS_1_4, FULL, CASES
from .utils import human_time, validate_password
from .crypto import fingerprint, make_record, check_record
from .dictionary import dictionary_attack, build_wordlist
from .brute_force import brute_force
from .attacks import combined_attack
from .protection import strength_problems, LoginGuard

__all__ = [
    "BINARY", "DIGITS_1_4", "FULL", "CASES",
    "human_time", "validate_password",
    "fingerprint", "make_record", "check_record",
    "dictionary_attack", "build_wordlist",
    "brute_force", "combined_attack",
    "strength_problems", "LoginGuard",
]