#!/usr/bin/env python3

import os
import sys
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
RAVEN = os.path.join(BASE, "raven.png")

def raven_fail():
    print("Kabul etmesende mahçupsun - r4ven.leet. Fotoğrafımı geri yükle")
    sys.exit(1)

if not os.path.isfile(RAVEN):
    raven_fail()

try:
    if os.path.getsize(RAVEN) < 1024:
        raven_fail()
    with Image.open(RAVEN) as img:
        img.verify()
except:
    raven_fail()

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import subprocess
import traceback
from typing import Optional

from rudy_runtime.sherlock import parse_sherlock_output, sherlock_command
from rudy_runtime.validation import clamp_timeout, clean_username

SITES_TO_CHECK = [
    "Instagram",
    "TikTok",
    "Facebook",
    "Snapchat",
    "Twitter",
    "Reddit",
    "Pinterest",
    "LinkedIn",
    "GitHub",
    "YouTube",
    "Twitch",
    "Kick",
    "Chess.com",
    "Lichess",
    "Steam",
    "Xbox Gamertag",
    "NameMC",
    "Spotify",
    "SoundCloud",
    "Telegram",
    "Duolingo",
    "Tinder",
    "HackerNews",
    "EksiSozluk",
    "Uludag",
]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Each search starts a Sherlock process that makes dozens of HTTP requests; cap how many run at once
MAX_CONCURRENT_SEARCHES = 2
search_slots = asyncio.Semaphore(MAX_CONCURRENT_SEARCHES)

async def sync_commands():
    # setup_hook runs once per process; on_ready fires again on every reconnect
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

bot.setup_hook = sync_commands

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

@bot.tree.command(name="username", description="Search for a username across multiple platforms using Sherlock")
@app_commands.describe(
    username="The username to search for",
    timeout="Search timeout in seconds (default: 60)"
)
async def username_search(
    interaction: discord.Interaction,
    username: str,
    timeout: Optional[int] = 60
):
    username = clean_username(username)
    if username is None:
        await interaction.response.send_message(
            "❌ Username must be 3-30 characters: letters, numbers, '.', '_' or '-', not starting with '-'.", ephemeral=True
        )
        return

    await interaction.response.defer(thinking=True)
    timeout = clamp_timeout(timeout)

    try:
        embed = discord.Embed(
            title=f"🔍 Searching for: {username}",
            description=f"Checking {len(SITES_TO_CHECK)} platforms...",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed)

        cmd = sherlock_command() + [username, "--timeout", "10"]
        for site in SITES_TO_CHECK:
            cmd.extend(["--site", site])

        async with search_slots:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                await interaction.followup.send(f"⏱️ Search for **{username}** took longer than {timeout} seconds and was stopped.")
                return
        output = stdout.decode("utf-8", errors="ignore")

        found = parse_sherlock_output(output)

        if process.returncode != 0 and not found:
            # A missing or broken Sherlock install used to look like "No Results"
            print(f"Sherlock exited with {process.returncode}: {stderr.decode('utf-8', errors='ignore')[-500:]}")
            await interaction.followup.send(embed=discord.Embed(
                title="❌ Search failed",
                description="Sherlock could not run on the server. Check that sherlock-project is installed.",
                color=discord.Color.red()
            ))
            return

        if found:
            embed = discord.Embed(
                title=f"✅ Found {len(found)} matches for: {username}",
                color=discord.Color.green()
            )
            for s in found[:20]:
                embed.add_field(name=s["name"], value=s["url"], inline=True)
            if len(found) > 20:
                embed.set_footer(text=f"{len(found) - 20} more matches not shown")
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(embed=discord.Embed(
                title="❌ No Results",
                description=f"No profiles found for **{username}**",
                color=discord.Color.red()
            ))

    except Exception:
        # Keep internal details (paths, command lines) in the log, not in the channel
        traceback.print_exc()
        await interaction.followup.send(embed=discord.Embed(
            title="❌ Error",
            description="Something went wrong while searching. Please try again later.",
            color=discord.Color.red()
        ))

if __name__ == "__main__":
    from rudy_runtime.config import load_config
    config = load_config({'TOKEN':'DISCORD_TOKEN'})
    if '--check-config' in sys.argv:
        subprocess.run(sherlock_command() + ['--version'], check=True)
        print('Configuration and dependencies ready')
        raise SystemExit(0)
    bot.run(config['TOKEN'])
