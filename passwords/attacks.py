"""Attaque combinée : dictionnaire d'abord, force brute ensuite."""
from .dictionary import dictionary_attack
from .brute_force import brute_force


def combined_attack(target_hash, charset, length, max_attempts=5_000_000):
    found, t1, s1 = dictionary_attack(target_hash)
    if found is not None:
        return found, t1, s1, "dictionnaire"
    found, t2, s2 = brute_force(target_hash, charset, length,
                                 max_attempts=max_attempts)
    return found, t1 + t2, s1 + s2, "force brute (dictionnaire épuisé)"