<p align="center"><img src="docs/banner.svg" alt="Rudy Username OSINT — Public username discovery through Sherlock and Discord." width="100%"></p>

<p align="center">
  <img src="https://img.shields.io/badge/Runtime-Python%20%2F%20Sherlock-55e0b6?style=flat-square&labelColor=101b28" alt="Python / Sherlock">
  <img src="https://img.shields.io/badge/Docs-source_reviewed-55e0b6?style=flat-square&labelColor=101b28" alt="Documentation based on source review">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-55e0b6?style=flat-square&labelColor=101b28" alt="MIT license"></a>
</p>

<p align="center"><strong>Public username discovery through Sherlock and Discord.</strong></p>

<p align="center"><a href="#overview">Overview</a> · <a href="#capabilities">Capabilities</a> · <a href="#quick-start">Quick start</a> · <a href="#implementation-notes">Implementation notes</a></p>

---

## Overview

A Discord wrapper around Sherlock. The `/username` command runs Sherlock against a configured list of 25 platform names, parses candidate profile links from its output and displays up to 20 matches in an embed.

## Capabilities

| Layer | Implemented behavior |
| :--- | :--- |
| Search | Invokes Sherlock as an asynchronous subprocess with selected `--site` values |
| Input | Accepts 3-30 letters, digits, `.`, `_` or `-`, never starting with `-` |
| Results | Parses Sherlock stdout, drops duplicate URLs, shows 20 matches and counts the rest |
| Discord | `/username` with an optional overall timeout, kept between 15 and 180 seconds |
| Errors | Reports a failed Sherlock run or timeout; internal errors go to the log, not the channel |

## Quick start

Requires Python, a Discord bot application and a Sherlock installation accessible to the bot process. Keep the bundled `raven.png`; it must be a readable image of at least 1 KB.

```bash
git clone https://github.com/r4venrudy/rudy-username-osint.git
cd rudy-username-osint
python -m pip install discord.py Pillow sherlock-project
sherlock --version
```

Set `DISCORD_TOKEN` in the process environment, or supply `TOKEN` in a local JSON file referenced by `RUDY_CONFIG`. Do not commit your configured token. No privileged intents are needed; invite the bot with `bot` and `applications.commands` scopes.

```bash
python bot.py
```

Use `/username username:example_user timeout:60` in Discord.

## Implementation notes

- Sherlock's site identifiers and output format can change. The configured platform names must match the installed Sherlock version.
- A matching username is a lead, not proof that profiles belong to the same person. Findings need verification in context.
- Usernames are checked against a strict allowlist, and a leading `-` is refused so Sherlock never reads the name as an option. The subprocess is passed an argument list rather than a shell command.
- The command uses a 10-second Sherlock per-request timeout and a separate overall wait. When the overall wait runs out the Sherlock process is killed. Concurrent command limits need review before operating a busy bot.
- No platform sign-in, private-profile access or identity attribution is implemented. Replies are channel-visible.

## Project map

```text
bot.py      Discord command, Sherlock runner and output parser
raven.png   Required startup asset
LICENSE     MIT license
```

## GitHub package

A non-root container is published to GitHub Packages after build and offline configuration checks. Credentials are supplied at runtime and are excluded from the image.

```sh
cp .env.example .env
# Fill in your own values in .env, keeping that file private.
docker run --rm --env-file .env ghcr.io/r4venrudy/rudy-username-osint:latest --check-config
docker run --rm --env-file .env ghcr.io/r4venrudy/rudy-username-osint:latest
```

`--check-config` validates installed dependencies, the bundled asset, and required settings without connecting to Discord. `RUDY_CONFIG` optionally points to a mounted JSON configuration file; environment variables take priority.

Only public project files are packaged. Image tags are `latest` and `sha-<full commit SHA>`. Discord login and external API behavior still require your own account configuration; CI never uses live credentials.


## License

[MIT](LICENSE). Preserve the attribution in the license file.

---

<p align="center">Part of the <a href="https://github.com/r4venrudy">r4venrudy</a> project collection.</p>
