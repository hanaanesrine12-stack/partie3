"""
Crypto module (previously hashing.py).
Handles password storage using the César cipher.
"""
import os
import time

from .caesar import (
    encrypt_password, verify_password, derive_key,
    caesar_encrypt, MASTER, PEPPER,
)

SALT_BYTES = 16

# Fixed salt used ONLY for the Zone-C offline attack demo.
_DEMO_SALT = b"\x00" * SALT_BYTES


# =========================================================================
# Demo fingerprints used by brute_force.py / dictionary.py / app.py
# =========================================================================
def fingerprint(password):
    """Deterministic fingerprint used for the offline attack demo."""
    key = derive_key(_DEMO_SALT)
    return caesar_encrypt(password, key).encode("latin-1").hex()

def fingerprint_bytes(password):
    """Binary version of fingerprint() for fast comparison in tight loops."""
    key = derive_key(_DEMO_SALT)
    return caesar_encrypt(password, key).encode("latin-1")


# =========================================================================
# Real credential storage (Zone A)
# =========================================================================
def make_record(password, iterations=None):
    """Build the record stored in the database."""
    salt = os.urandom(SALT_BYTES)
    ciphertext = encrypt_password(password, salt)
    return {
        "algo": "cesar",
        "salt": salt,
        "hash": ciphertext,          # field name kept for app.py compatibility
        "iterations": 0,
    }

def check_record(record, guess):
    """Verify a candidate password against a stored record."""
    return verify_password(guess, record["salt"], record["hash"])