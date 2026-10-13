import re
import shutil
import sys

# Sherlock prints hits as "[+] Site Name: https://..."
_HIT = re.compile(r"^\[\+\]\s*([^:]+):\s*(https?://\S+)")


_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def parse_sherlock_output(output):
    """Return [{"name", "url"}] for each profile Sherlock reported as found, without duplicates."""
    found, seen = [], set()
    # colour codes would hide the "[+]" marker if colorama ever leaves them in
    for line in _ANSI.sub("", output).splitlines():
        m = _HIT.match(line.strip())
        if m and m.group(2) not in seen:
            seen.add(m.group(2))
            found.append({"name": m.group(1).strip(), "url": m.group(2)})
    return found


def sherlock_command(which=shutil.which):
    """Return the argv prefix that runs Sherlock: the console script if present, else the module."""
    return ["sherlock"] if which("sherlock") else [sys.executable, "-m", "sherlock_project"]


def results_text(username, found):
    """Plain-text report of every match, attached when the embed cannot show them all."""
    lines = [f"Sherlock matches for {username} ({len(found)})", ""]
    lines += [f"{s['name']}: {s['url']}" for s in found]
    return "\n".join(lines) + "\n"
