import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import subprocess
import re
from typing import Optional

# Predefined list of sites to search
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
    "NameMC",  # Minecraft
    "Spotify",
    "SoundCloud",
    "Telegram",
    "Duolingo",
    "Tinder",
    "HackerNews",
    # Turkish sites
    "EksiSozluk",  # Turkish forum
    "Uludag",  # Turkish forum
]

# Bot setup
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
    """Performs OSINT username search using Sherlock"""
    
    # Defer the response since this will take time
    await interaction.response.defer(thinking=True)
    
    # Validate username
    if not username.isalnum() and not any(c in username for c in ['_', '-', '.']):
        await interaction.followup.send("❌ Invalid username format. Use alphanumeric characters, underscores, hyphens, or periods.")
        return
    
    if len(username) < 3 or len(username) > 30:
        await interaction.followup.send("❌ Username must be between 3 and 30 characters.")
        return
    
    try:
        # Create embed for initial status
        status_embed = discord.Embed(
            title=f"🔍 Searching for: {username}",
            description=f"Checking {len(SITES_TO_CHECK)} platforms...\n\nThis should take 30-60 seconds.",
            color=discord.Color.blue()
        )
        status_msg = await interaction.followup.send(embed=status_embed)
        
        # Determine the correct command to use
        try:
            subprocess.run(["sherlock", "--version"], capture_output=True, check=True, timeout=5)
            base_cmd = ["sherlock"]
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            # Try python3 first (Linux/Mac), then python (Windows)
            try:
                subprocess.run(["python3", "--version"], capture_output=True, check=True, timeout=5)
                base_cmd = ["python3", "-m", "sherlock"]
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                base_cmd = ["python", "-m", "sherlock"]
        
        # Run Sherlock command - just get text output
        cmd = base_cmd + [username, "--timeout", str(10)]
        
        # Add predefined sites
        for site in SITES_TO_CHECK:
            cmd.extend(["--site", site])
        
        print(f"Running command: {' '.join(cmd)}")
        print(f"Checking {len(SITES_TO_CHECK)} sites")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for the process with timeout
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout + 30
            )
        except asyncio.TimeoutError:
            process.kill()
            raise asyncio.TimeoutError(f"Sherlock process exceeded {timeout + 30} seconds")
        
        output = stdout.decode('utf-8', errors='ignore')
        error_output = stderr.decode('utf-8', errors='ignore')
        
        print(f"=== STDOUT ===\n{output}\n")
        print(f"=== STDERR ===\n{error_output}\n")
        
        # Parse the output to find URLs
        found_sites = []
        lines = output.split('\n')
        
        for line in lines:
            # Look for lines with URLs (Sherlock format: [+] Site: URL)
            if 'http' in line.lower() and ('[+]' in line or '[*]' in line):
                # Extract site name and URL
                match = re.search(r'\[.\]\s*([^:]+):\s*(https?://[^\s]+)', line)
                if match:
                    site_name = match.group(1).strip()
                    url = match.group(2).strip()
                    found_sites.append({
                        'name': site_name,
                        'url': url
                    })
                else:
                    # Try alternate format - just find any URL in the line
                    url_match = re.search(r'(https?://[^\s]+)', line)
                    if url_match:
                        url = url_match.group(1).strip()
                        # Extract site name from URL
                        site_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
                        site_name = site_match.group(1) if site_match else "Unknown"
                        found_sites.append({
                            'name': site_name,
                            'url': url
                        })
        
        # Create result embeds
        if found_sites:
            # Split results into chunks for multiple embeds (Discord limit: 25 fields per embed)
            chunk_size = 20
            for i in range(0, len(found_sites), chunk_size):
                chunk = found_sites[i:i + chunk_size]
                
                result_embed = discord.Embed(
                    title=f"✅ Found {len(found_sites)} matches for: {username}",
                    description=f"Results {i+1}-{min(i+chunk_size, len(found_sites))} of {len(found_sites)}",
                    color=discord.Color.green()
                )
                
                for site in chunk:
                    result_embed.add_field(
                        name=site['name'],
                        value=f"[Profile Link]({site['url']})",
                        inline=True
                    )
                
                result_embed.set_footer(text=f"Requested by {interaction.user.display_name}")
                await interaction.followup.send(embed=result_embed)
        else:
            not_found_embed = discord.Embed(
                title=f"❌ No Results",
                description=f"No profiles found for username: **{username}**\n\nThis could mean:\n• Username doesn't exist on searched platforms\n• Username search timed out\n• Sherlock encountered errors",
                color=discord.Color.red()
            )
            
            # Add raw output for debugging if it's short enough
            if len(output) < 500:
                not_found_embed.add_field(name="Debug Output", value=f"```{output[:500]}```", inline=False)
            
            await interaction.followup.send(embed=not_found_embed)
            
    except asyncio.TimeoutError:
        timeout_embed = discord.Embed(
            title="⏱️ Timeout",
            description=f"Search exceeded {timeout} seconds timeout.",
            color=discord.Color.orange()
        )
        await interaction.followup.send(embed=timeout_embed)
    except FileNotFoundError:
        install_embed = discord.Embed(
            title="❌ Sherlock Not Found",
            description="Sherlock is not installed. Install it with:\n```pip install sherlock-project```",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=install_embed)
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=error_embed)
        print(f"Exception: {e}")

# Run the bot
if __name__ == "__main__":
    TOKEN = "YOUR DISCORD BOT TOKEN HERE"
    bot.run(TOKEN)