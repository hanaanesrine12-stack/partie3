"""Petites fonctions utilitaires partagées."""

def human_time(seconds):
    if seconds is None:
        return "n/a"
    if seconds == float("inf") or seconds >= 1e18:
        return "pratiquement infini"
    if seconds < 1e-3:
        return "instantané"
    if seconds < 1:
        return "%.3f s" % seconds
    if seconds < 60:
        return "%.2f s" % seconds
    if seconds < 3600:
        return "%.1f min" % (seconds / 60)
    if seconds < 86400:
        return "%.1f h" % (seconds / 3600)
    if seconds < 86400 * 365:
        return "%.1f jours" % (seconds / 86400)
    if seconds < 86400 * 365 * 1e6:
        return "%.1f ans" % (seconds / (86400 * 365))
    return "%.2e ans" % (seconds / (86400 * 365))


def search_space(charset, length):
    return len(charset) ** length


def estimate_seconds(space, rate):
    if not rate:
        return float("inf")
    return space / rate


def validate_password(password, charset, length=None):
    """Validation d'un mot de passe saisi (utilisé par app.py)."""
    if not password:
        return False, "Le mot de passe ne peut pas être vide."
    if length is not None and len(password) != length:
        return False, "Le mot de passe doit avoir %d caractères." % length
    if not set(password) <= set(charset):
        return False, "Caractères autorisés : %s" % charset
    return True, ""