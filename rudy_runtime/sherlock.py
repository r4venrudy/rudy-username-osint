import re
import shutil
import sys

# Sherlock prints hits as "[+] Site Name: https://..."
_HIT = re.compile(r"^\[\+\]\s*([^:]+):\s*(https?://\S+)")


def parse_sherlock_output(output):
    """Return [{"name", "url"}] for each profile Sherlock reported as found, without duplicates."""
    found, seen = [], set()
    for line in output.splitlines():
        m = _HIT.match(line.strip())
        if m and m.group(2) not in seen:
            seen.add(m.group(2))
            found.append({"name": m.group(1).strip(), "url": m.group(2)})
    return found


def sherlock_command(which=shutil.which):
    """Return the argv prefix that runs Sherlock: the console script if present, else the module."""
    return ["sherlock"] if which("sherlock") else [sys.executable, "-m", "sherlock_project"]
