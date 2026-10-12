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
import shutil
import subprocess
from typing import Optional

from rudy_runtime.sherlock import parse_sherlock_output
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
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

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

        # shutil.which is instant; the old subprocess probes blocked the event loop for up to 10 seconds
        base_cmd = ["sherlock"] if shutil.which("sherlock") else [sys.executable, "-m", "sherlock_project"]

        cmd = base_cmd + [username, "--timeout", "10"]
        for site in SITES_TO_CHECK:
            cmd.extend(["--site", site])

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            await interaction.followup.send(f"⏱️ Search for **{username}** took longer than {timeout} seconds and was stopped.")
            return
        output = stdout.decode("utf-8", errors="ignore")

        found = parse_sherlock_output(output)

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

    except Exception as e:
        await interaction.followup.send(embed=discord.Embed(
            title="❌ Error",
            description=str(e),
            color=discord.Color.red()
        ))

if __name__ == "__main__":
    from rudy_runtime.config import load_config
    config = load_config({'TOKEN':'DISCORD_TOKEN'})
    if '--check-config' in sys.argv:
        subprocess.run(['sherlock', '--version'], check=True)
        print('Configuration and dependencies ready')
        raise SystemExit(0)
    bot.run(config['TOKEN'])
