"""Input checks for the /username command."""

import re

USERNAME_RE = re.compile(r"[A-Za-z0-9._-]{3,30}")

MIN_TIMEOUT = 15
MAX_TIMEOUT = 180
DEFAULT_TIMEOUT = 60


def clean_username(raw):
    """Return the stripped username, or None if it is not 3-30 safe characters."""
    name = (raw or "").strip()
    return name if USERNAME_RE.fullmatch(name) else None


def clamp_timeout(value):
    """Keep the overall search timeout between MIN_TIMEOUT and MAX_TIMEOUT seconds."""
    return max(MIN_TIMEOUT, min(value or DEFAULT_TIMEOUT, MAX_TIMEOUT))
