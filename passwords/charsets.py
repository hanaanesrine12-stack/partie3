"""Alphabets et définition des 3 cas du sujet."""
import string

# Cas 1 : {0, 1}
BINARY = "01"

# Cas 2 : {1, 2, 3, 4}
DIGITS_1_4 = "1234"

# Cas 3 : minuscules + majuscules + chiffres + symboles usuels
FULL = string.ascii_letters + string.digits + "+*-_!@#$%&()=?"

# Cas exposés à l'interface : (alphabet, longueur)
CASES = {
    "3 caractères, chacun 0 ou 1":      (BINARY, 3),
    "4 caractères, chacun de 1 à 4":    (DIGITS_1_4, 4),
    "caractères a-z A-Z 0-9 + * ...":   (FULL, None),
}