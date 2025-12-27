#!/usr/bin/env python3
"""
Discord Bot for JS-Scanner VPS Control
Executes scan commands in a screen session on the VPS
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "0"))
WORK_DIR = os.getenv("JSSCANNER_PATH", "/home/sl4x0/js-scanner")
SCREEN_SESSION_NAME = "discord"
# ---------------------

# Validate configuration
if not BOT_TOKEN:
    raise ValueError("❌ DISCORD_BOT_TOKEN not found in environment variables!")
if AUTHORIZED_USER_ID == 0:
    raise ValueError("❌ AUTHORIZED_USER_ID not found in environment variables!")

# Setup Bot
intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)


@client.event
async def on_ready():
    print(f'✅ Bot logged in as {client.user} (ID: {client.user.id})', flush=True)
    print(f'📂 Working directory: {WORK_DIR}', flush=True)
    print(f'👤 Authorized user ID: {AUTHORIZED_USER_ID}', flush=True)
    print(f'🖥️  Screen session name: {SCREEN_SESSION_NAME}', flush=True)
    
    try:
        synced = await client.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s)", flush=True)
        print(f"🎯 Commands: {', '.join([cmd.name for cmd in synced])}", flush=True)
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}", flush=True)


@client.tree.command(name="scan", description="Execute a JS-Scanner command in the 'discord' screen session")
@app_commands.describe(
    full_command="The full command (e.g., python3 -m jsscanner -t target.com --subjs --no-live -u https://example.com)"
)
async def scan(interaction: discord.Interaction, full_command: str):
    """Execute a full JS-Scanner command in a detached screen session"""
    
    # 1. Security Check
    if interaction.user.id != AUTHORIZED_USER_ID:
        await interaction.response.send_message(
            "⛔ **Unauthorized.** Only the VPS owner can run scans.", 
            ephemeral=True
        )
        return
    
    # 2. Validate command (basic safety check)
    if not full_command.strip():
        await interaction.response.send_message(
            "❌ **Error:** Command cannot be empty.", 
            ephemeral=True
        )
        return
    
    # 3. Check if screen session exists
    check_screen = await asyncio.create_subprocess_shell(
        f"screen -list | grep -q {SCREEN_SESSION_NAME}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await check_screen.communicate()
    screen_exists = (check_screen.returncode == 0)
    
    # 4. Execute command in screen
    try:
        if screen_exists:
            # Send command to existing screen session
            # -X stuff: Send keystrokes to screen session
            screen_cmd = (
                f"screen -S {SCREEN_SESSION_NAME} -X stuff "
                f"'cd {WORK_DIR} && {full_command}\\n'"
            )
        else:
            # Create new detached screen session
            safe_command = full_command.replace("'", "'\\''")
            screen_cmd = (
                f"screen -dmS {SCREEN_SESSION_NAME} bash -c '"
                f"cd {WORK_DIR} && "
                f"{safe_command}; "
                f"echo \"[Scan Complete - $(date)]\"; "
                f"exec bash'"
            )
        
        # 5. Execute the command
        process = await asyncio.create_subprocess_shell(
            screen_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        # 6. Send confirmation embed
        status = "reused existing" if screen_exists else "created new"
        embed = discord.Embed(
            title="🚀 Scan Launched",
            description=f"Command executed in screen session `{SCREEN_SESSION_NAME}` ({status})",
            color=discord.Color.green()
        )
        embed.add_field(
            name="📂 Directory",
            value=f"`{WORK_DIR}`",
            inline=False
        )
        embed.add_field(
            name="💻 Command",
            value=f"```bash\n{full_command[:1000]}{'...' if len(full_command) > 1000 else ''}\n```",
            inline=False
        )
        embed.add_field(
            name="ℹ️ Note",
            value="Notifications will be sent by the scanner's webhook as usual.",
            inline=False
        )
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)
        
        if stderr:
            error_msg = stderr.decode('utf-8')[:500]
            if error_msg.strip():
                print(f"⚠️ Screen command stderr: {error_msg}")
    
    except Exception as e:
        await interaction.response.send_message(
            f"❌ **Error launching screen session:**\n```\n{str(e)[:1000]}\n```",
            ephemeral=True
        )
        print(f"❌ Exception in /scan: {e}")


@client.tree.command(name="screen-status", description="Check if the 'discord' screen session is running")
async def screen_status(interaction: discord.Interaction):
    """Check the status of the screen session"""
    
    # Security check
    if interaction.user.id != AUTHORIZED_USER_ID:
        await interaction.response.send_message(
            "⛔ **Unauthorized.**", 
            ephemeral=True
        )
        return
    
    try:
        # Check if screen session exists
        process = await asyncio.create_subprocess_shell(
            f"screen -list | grep {SCREEN_SESSION_NAME}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0 and stdout:
            # Session exists
            session_info = stdout.decode('utf-8').strip()
            embed = discord.Embed(
                title="✅ Screen Session Active",
                description=f"Session `{SCREEN_SESSION_NAME}` is running",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Session Info",
                value=f"```\n{session_info}\n```",
                inline=False
            )
            embed.add_field(
                name="How to Attach",
                value=f"```bash\nscreen -r {SCREEN_SESSION_NAME}\n```\n*(Ctrl+A, then D to detach)*",
                inline=False
            )
        else:
            # Session doesn't exist
            embed = discord.Embed(
                title="⚪ No Active Session",
                description=f"Screen session `{SCREEN_SESSION_NAME}` is not running",
                color=discord.Color.light_gray()
            )
            embed.add_field(
                name="ℹ️ Note",
                value="Use `/scan` to start a new scan, which will create the session.",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    except Exception as e:
        await interaction.response.send_message(
            f"❌ **Error checking screen status:**\n```\n{str(e)[:1000]}\n```",
            ephemeral=True
        )


@client.tree.command(name="screen-list", description="List all active screen sessions")
async def screen_list(interaction: discord.Interaction):
    """List all screen sessions on the VPS"""
    
    # Security check
    if interaction.user.id != AUTHORIZED_USER_ID:
        await interaction.response.send_message(
            "⛔ **Unauthorized.**", 
            ephemeral=True
        )
        return
    
    try:
        process = await asyncio.create_subprocess_shell(
            "screen -list",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        output = stdout.decode('utf-8').strip()
        
        if not output or "No Sockets found" in output:
            embed = discord.Embed(
                title="📋 Screen Sessions",
                description="No active screen sessions found.",
                color=discord.Color.light_gray()
            )
        else:
            embed = discord.Embed(
                title="📋 Active Screen Sessions",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Sessions",
                value=f"```\n{output[:1000]}\n```",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    except Exception as e:
        await interaction.response.send_message(
            f"❌ **Error listing screens:**\n```\n{str(e)[:1000]}\n```",
            ephemeral=True
        )


@client.tree.command(name="help", description="Show bot usage instructions")
async def help_command(interaction: discord.Interaction):
    """Display help information"""
    
    embed = discord.Embed(
        title="🤖 JS-Scanner Discord Bot",
        description="Remote control for your VPS JS-Scanner tool",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="/scan <full_command>",
        value=(
            "Execute a JS-Scanner command in screen session.\n"
            "**Example:**\n"
            "```\n/scan python3 -m jsscanner -t example.com --subjs --no-live -u https://example.com\n```"
        ),
        inline=False
    )
    
    embed.add_field(
        name="/screen-status",
        value="Check if the 'discord' screen session is running",
        inline=False
    )
    
    embed.add_field(
        name="/screen-list",
        value="List all active screen sessions on the VPS",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ How It Works",
        value=(
            f"• Commands run in screen session `{SCREEN_SESSION_NAME}`\n"
            f"• Working directory: `{WORK_DIR}`\n"
            "• Notifications sent via scanner's webhook\n"
            f"• Attach to session: `screen -r {SCREEN_SESSION_NAME}`"
        ),
        inline=False
    )
    
    embed.set_footer(text="Only authorized users can execute commands")
    
    await interaction.response.send_message(embed=embed)


# Error handler
@client.event
async def on_command_error(ctx, error):
    print(f"❌ Command error: {error}")


# Start the bot
if __name__ == "__main__":
    print("🤖 Starting JS-Scanner Discord Bot...")
    print(f"📝 Config check: BOT_TOKEN={'✅ Set' if BOT_TOKEN else '❌ Missing'}")
    print(f"📝 Config check: AUTHORIZED_USER_ID={'✅ Set' if AUTHORIZED_USER_ID else '❌ Missing'}")
    
    try:
        client.run(BOT_TOKEN)
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
