# modules/pi_cmd.py
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
    await ctx.channel.send(f"🚀 Checking status...")
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
    text = (
        f"\n```bash\n**💻CPU:** {cpu}%\n"
        f"**🧠RAM:** {mem.percent}% (usable {mem.available // (1024*1024)} MB)\n"
        f"**💾Disk:** {disk.percent}% ({disk.used // (1024*1024*1024)}GB/{disk.total // (1024*1024*1024)}GB)\n"
        f"**⏱️Uptime:** {str(uptime).split('.')[0]}\n```"
    )
    await ctx.channel.send(f"{text}")

# --- !docker ps: Show all container Docker are running ---
async def docker_ps(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.channel.send(f"⛔️You are not allowed to use this command.")
    await ctx.channel.send(f"🐳 Checking container...")
    try:
        output = subprocess.run(['docker', 'ps'], capture_output=True, text=True, check=True)
        msg = output.stdout
        if not msg:
            msg = "(No container is running.)"
        await send_long_message(ctx.channel, msg)
    except subprocess.CalledProcessError as e:
        await send_long_message(ctx.channel, "Error occurred while checking container.")

# --- !update: Git pull and restart bot ---
async def update(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.channel.send(f"⛔️You are not allowed to use this command.")

    await ctx.channel.send("📦 Pulling latest code & rebuilding bot...")
    try:
        response = requests.post("http://update-manager:20000/update")
        data = response.json()

        output = data.get("output", "No output")
        snippet = output[:1900] + ("… (truncated)" if len(output) > 1900 else "")
        if response.status_code == 200:
            await ctx.channel.send(f"\n```bash\n{snippet}\n```")
        else:
            await ctx.channel.send(f"❌ Error: {snippet}")

    except subprocess.CalledProcessError as e:
        error_output = e.stderr or e.stdout or "Unknown error"
        snippet = error_output[:1900] + ("… (truncated)" if len(error_output) > 1900 else "")
        await ctx.channel.send(
            f"❌ Update failed (exit code {e.returncode}):\n```bash\n{snippet}\n```"
        )

async def send_long_message(channel, content, prefix="```bash\n", suffix="```"):
    max_len = 2000 - len(prefix) - len(suffix)
    for i in range(0, len(content), max_len):
        part = content[i:i + max_len]
        await channel.send(f"{prefix}{part}{suffix}")