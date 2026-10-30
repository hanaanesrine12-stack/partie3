"""Attaque par force brute — compare les digests (plus rapide)."""
import itertools
import time
from .crypto import fingerprint_bytes


def brute_force(target_hash, charset, length, max_attempts=None):
    target = bytes.fromhex(target_hash)
    start = time.perf_counter()
    attempts = 0
    for tup in itertools.product(charset, repeat=length):
        attempts += 1
        if fingerprint_bytes("".join(tup)) == target:
            return "".join(tup), attempts, time.perf_counter() - start
        if max_attempts is not None and attempts >= max_attempts:
            break
    return None, attempts, time.perf_counter() - start