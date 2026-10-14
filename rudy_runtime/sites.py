"""Sites passed to Sherlock with --site. Names must match entries in Sherlock's data.json exactly
(case-insensitive); Sherlock silently skips unknown names, so tests check them against the installed list."""

SITES_TO_CHECK = [
    "Instagram",
    "TikTok",
    "Snapchat",
    "Twitter",
    "Reddit",
    "Pinterest",
    "LinkedIn",
    "GitHub",
    "YouTube",
    "Twitch",
    "Kick",
    "Chess",
    "Lichess",
    "Steam Community (User)",
    "Xbox Gamertag",
    "Minecraft",
    "Spotify",
    "SoundCloud",
    "Telegram",
    "Duolingo",
    "HackerNews",
]


def pick_sites(text):
    """Turn an optional "github, reddit" filter into Sherlock site names.

    Returns (sites, unknown): matching is case-insensitive against SITES_TO_CHECK, an empty filter means
    every site, and names that are not on the list are returned so the user can be told.
    """
    if not text or not text.strip():
        return list(SITES_TO_CHECK), []
    by_lower = {s.lower(): s for s in SITES_TO_CHECK}
    sites, unknown = [], []
    for part in text.split(","):
        name = part.strip()
        if not name:
            continue
        match = by_lower.get(name.lower())
        if match and match not in sites:
            sites.append(match)
        elif not match:
            unknown.append(name)
    return sites, unknown
