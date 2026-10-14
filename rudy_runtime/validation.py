"""Input checks for the /username command."""

import re

# The first character may not be "-" so Sherlock never reads the name as an option such as --version.
USERNAME_RE = re.compile(r"[A-Za-z0-9._][A-Za-z0-9._-]{2,29}")

MIN_TIMEOUT = 15
MAX_TIMEOUT = 180
DEFAULT_TIMEOUT = 60


def clean_username(raw):
    """Return the stripped username, or None if it is not 3-30 safe characters.

    A leading "@" (as copied from a profile, "@name") is dropped.
    """
    name = (raw or "").strip()
    if name.startswith("@"):
        name = name[1:]
    return name if USERNAME_RE.fullmatch(name) else None


def clamp_timeout(value):
    """Keep the overall search timeout between MIN_TIMEOUT and MAX_TIMEOUT seconds."""
    return max(MIN_TIMEOUT, min(value or DEFAULT_TIMEOUT, MAX_TIMEOUT))
