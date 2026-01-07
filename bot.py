import os
import sys
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import subprocess
import re
from typing import Optional

REQUIRED_FILE = "raven.png"

def raven_guard():
    if not os.path.isfile(REQUIRED_FILE):
        print("critical file missing")
        sys.exit(1)

raven_guard()

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
    print(f'{bot.user} has connected to Discord!')
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

    if not username.isalnum() and not any(c in username for c in ['_', '-', '.']):
        await interaction.followup.send("❌ Invalid username format. Use alphanumeric characters, underscores, hyphens, or periods.")
        return

    if len(username) < 3 or len(username) > 30:
        await interaction.followup.send("❌ Username must be between 3 and 30 characters.")
        return

    try:
        status_embed = discord.Embed(
            title=f"🔍 Searching for: {username}",
            description=f"Checking {len(SITES_TO_CHECK)} platforms...\n\nThis should take 30-60 seconds.",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=status_embed)

        try:
            subprocess.run(["sherlock", "--version"], capture_output=True, check=True, timeout=5)
            base_cmd = ["sherlock"]
        except Exception:
            try:
                subprocess.run(["python3", "--version"], capture_output=True, check=True, timeout=5)
                base_cmd = ["python3", "-m", "sherlock"]
            except Exception:
                base_cmd = ["python", "-m", "sherlock"]

        cmd = base_cmd + [username, "--timeout", "10"]

        for site in SITES_TO_CHECK:
            cmd.extend(["--site", site])

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout + 30
        )

        output = stdout.decode("utf-8", errors="ignore")

        found_sites = []

        for line in output.split("\n"):
            if "http" in line.lower() and ("[+]" in line or "[*]" in line):
                match = re.search(r'\[.\]\s*([^:]+):\s*(https?://[^\s]+)', line)
                if match:
                    found_sites.append({
                        "name": match.group(1).strip(),
                        "url": match.group(2).strip()
                    })
                else:
                    url_match = re.search(r'(https?://[^\s]+)', line)
                    if url_match:
                        url = url_match.group(1).strip()
                        site_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
                        found_sites.append({
                            "name": site_match.group(1) if site_match else "Unknown",
                            "url": url
                        })

        if found_sites:
            chunk_size = 20
            for i in range(0, len(found_sites), chunk_size):
                chunk = found_sites[i:i + chunk_size]
                embed = discord.Embed(
                    title=f"✅ Found {len(found_sites)} matches for: {username}",
                    description=f"Results {i+1}-{min(i+chunk_size, len(found_sites))} of {len(found_sites)}",
                    color=discord.Color.green()
                )
                for site in chunk:
                    embed.add_field(
                        name=site["name"],
                        value=f"[Profile Link]({site['url']})",
                        inline=True
                    )
                embed.set_footer(text=f"Requested by {interaction.user.display_name}")
                await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ No Results",
                description=f"No profiles found for username: **{username}**",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    except asyncio.TimeoutError:
        await interaction.followup.send(embed=discord.Embed(
            title="⏱️ Timeout",
            description=f"Search exceeded {timeout} seconds timeout.",
            color=discord.Color.orange()
        ))
    except FileNotFoundError:
        await interaction.followup.send(embed=discord.Embed(
            title="❌ Sherlock Not Found",
            description="Install with: pip install sherlock-project",
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
