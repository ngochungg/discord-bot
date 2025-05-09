# modules/on_pi_cmd.py
import asyncio
import datetime
import os
import subprocess
from pathlib import Path

import psutil
import requests

from dotenv import load_dotenv

ALLOWED_USER_IDS = [377676460334514176]

# --- Setup bot ---
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# --- File path ---
__File__ = Path(__file__).parent.resolve()
project_dir = __File__.parent

# --- !status: Show CPU, RAM, Disk and time uptime ---
async def status(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.channel.send(f"⛔️You are not allowed to use this command.")

    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
    text = (
        f"**💻CPU:** {cpu}%\n"
        f"**🧠RAM:** {mem.percent}% (usable {mem.available // (1024*1024)} MB)\n"
        f"**💾Disk:** {disk.percent}% ({disk.used // (1024*1024*1024)}GB/{disk.total // (1024*1024*1024)}GB)\n"
        f"**⏱️Uptime:** {str(uptime).split('.')[0]}"
    )
    await ctx.channel.send(f"{text}")

# --- !docker ps: Show all container Docker are running ---
async def docker_ps(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.channel.send(f"⛔️You are not allowed to use this command.")

    try:
        output = subprocess.run(['docker', 'ps'], capture_output=True, text=True, check=True)
        msg = output.stdout
        if not msg:
            msg = "(No container is running.)"
        await ctx.channel.send(f"```bash\n{msg}\n```")
    except subprocess.CalledProcessError as e:
        await ctx.channel.send(f"Error while run docker ps: {e}")

# --- !reboot: Reboot Pi (only bot owner) ---
async def reboot(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.channel.send(f"⛔️You are not allowed to use this command.")

    await ctx.channel.send("🔄 Reboot system...")
    subprocess.Popen(['sudo reboot'])

# --- !shutdown: Shutdown Pi (only bot owner) ---
async def shutdown(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.channel.send(f"⛔️You are not allowed to use this command.")

    await ctx.channel.send("⏻ Shutdown system...")
    subprocess.Popen(['sudo shutdown', '-h', 'now'])

# --- !update: Git pull and restart bot ---
async def update(ctx):
    await ctx.channel.send("📦 Pulling latest code & rebuilding bot...")
    # run the script, capture both streams
    proc = subprocess.run(
        ["bash", "./update_bot.sh"],
        cwd="/app/update-manager",       # ensure correct working dir
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # choose which to show: prefer stderr if non-zero
    if proc.returncode != 0:
        out = proc.stderr or proc.stdout or "Unknown error"
        # truncate to 1900 chars so the message (with backticks) stays < 4000
        snippet = out[:1900] + ("… (truncated)" if len(out) > 1900 else "")
        print(out)
        await ctx.channel.send(f"❌ Update failed (exit {proc.returncode}):\n```bash\n{snippet}\n```")
    else:
        await ctx.channel.send("✅ Update completed successfully.")