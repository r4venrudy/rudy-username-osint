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
import re
from typing import Optional

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
    await interaction.response.defer(thinking=True)

    if not username.isalnum() and not any(c in username for c in ["_", "-", "."]):
        await interaction.followup.send("❌ Invalid username format.")
        return

    if len(username) < 3 or len(username) > 30:
        await interaction.followup.send("❌ Username must be between 3 and 30 characters.")
        return

    try:
        embed = discord.Embed(
            title=f"🔍 Searching for: {username}",
            description=f"Checking {len(SITES_TO_CHECK)} platforms...",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed)

        try:
            subprocess.run(["sherlock", "--version"], capture_output=True, check=True, timeout=5)
            base_cmd = ["sherlock"]
        except:
            try:
                subprocess.run(["python3", "--version"], capture_output=True, check=True, timeout=5)
                base_cmd = ["python3", "-m", "sherlock"]
            except:
                base_cmd = ["python", "-m", "sherlock"]

        cmd = base_cmd + [username, "--timeout", "10"]
        for site in SITES_TO_CHECK:
            cmd.extend(["--site", site])

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, _ = await asyncio.wait_for(process.communicate(), timeout=timeout + 30)
        output = stdout.decode("utf-8", errors="ignore")

        found = []

        for line in output.split("\n"):
            if "http" in line.lower() and ("[+]" in line or "[*]" in line):
                m = re.search(r"\[.\]\s*([^:]+):\s*(https?://[^\s]+)", line)
                if m:
                    found.append({"name": m.group(1), "url": m.group(2)})

        if found:
            embed = discord.Embed(
                title=f"✅ Found {len(found)} matches for: {username}",
                color=discord.Color.green()
            )
            for s in found[:20]:
                embed.add_field(name=s["name"], value=s["url"], inline=True)
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
    TOKEN = "YOUR DISCORD BOT TOKEN HERE"
    bot.run(TOKEN)
