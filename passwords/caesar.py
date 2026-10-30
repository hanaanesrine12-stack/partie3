"""
César cipher on printable ASCII + key-derivation function f.

Design summary
--------------
- Cipher     : generalized César on ASCII codes 32..126 (95 symbols).
- Key f      : h = (h * 31 + b) % 95, folded over MASTER || PEPPER || salt.
- Secrets    : MASTER and PEPPER live OUTSIDE the database (env vars).
- Stored     : {salt, ciphertext}.  The key is never written anywhere.

No stretching, no constant-time comparison — kept minimal on purpose.

WARNING (for the report)
------------------------
A cipher is reversible.  This design is the best possible under the
"cipher only, no hashing" constraint, but it is NOT production-grade.
Use PBKDF2 / bcrypt / Argon2 in real systems.
"""
import os

# --- Printable ASCII range -------------------------------------------------
ASCII_FIRST = 32          # space
ASCII_LAST  = 126         # '~'
ASCII_MOD   = ASCII_LAST - ASCII_FIRST + 1   # = 95

# --- Secrets (loaded from environment, NEVER from the database) ----------
# Set these before launching app.py, for example:
#   export SSAD_MASTER="a3f19c2b74e8d05f613b9a2c4f7e8d10"
#   export SSAD_PEPPER="5c8e21f0b9a4d7c3"
_DEFAULT_MASTER = "a3f19c2b74e8d05f613b9a2c4f7e8d10"
_DEFAULT_PEPPER = "5c8e21f0b9a4d7c3"


def _load_secret(name, default_hex):
    raw = os.environ.get(name, default_hex)
    return bytes.fromhex(raw)


MASTER = _load_secret("SSAD_MASTER", _DEFAULT_MASTER)
PEPPER = _load_secret("SSAD_PEPPER", _DEFAULT_PEPPER)


# =========================================================================
# César cipher on printable ASCII (32..126)
# =========================================================================
def caesar_encrypt(text, key):
    """Shift each character by key, modulo 95, inside ASCII 32..126."""
    k = key % ASCII_MOD
    out = []
    for ch in text:
        code = ord(ch)
        if ASCII_FIRST <= code <= ASCII_LAST:
            out.append(chr((code - ASCII_FIRST + k) % ASCII_MOD + ASCII_FIRST))
        else:
            out.append(ch)          # leave non-printable characters untouched
    return "".join(out)


def caesar_decrypt(text, key):
    """Inverse of caesar_encrypt."""
    return caesar_encrypt(text, -key % ASCII_MOD)


# =========================================================================
# Key-derivation function f(MASTER, PEPPER, salt) -> int in [0, 94]
# =========================================================================
def derive_key(salt):
    """
    h = (h * 31 + b) % 95   for each byte b in (MASTER || PEPPER || salt)
    Result is the César shift for this user.
    """
    h = 0
    for b in MASTER + PEPPER + salt:
        h = (h * 31 + b) % ASCII_MOD
    return h


# =========================================================================
# Public API used by hashing.py
# =========================================================================
def encrypt_password(password, salt):
    """Return the ciphertext bytes for storage (single César pass)."""
    key = derive_key(salt)
    return caesar_encrypt(password, key).encode("latin-1")


def verify_password(password, salt, stored_ciphertext):
    """Re-derive the key, re-encrypt the guess, compare bytes."""
    key = derive_key(salt)
    produced = caesar_encrypt(password, key).encode("latin-1")
    return produced == stored_ciphertext

def get_secrets():
    return MASTER.hex(), PEPPER.hex()