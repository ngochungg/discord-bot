# modules/pi_cmd.py
import asyncio
import datetime
import os
import subprocess
import aiohttp
import psutil
import requests

from pathlib import Path
from dotenv import load_dotenv
from utils.long_message import send_long_sys_message

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
        return

    await ctx.channel.send(f"🚀 Checking status...")

    # Basic info
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())

    # Network monitoring
    upload, download = await get_network_speed()
    if upload is None or download is None:
        net_text = "Không lấy được thông tin mạng."
    else:
        net_text = f"⬆ {upload} KB/s | ⬇ {download} KB/s"

    text = (
        f"\n```bash\n"
        f"💻 CPU:     {cpu}%\n"
        f"🧠 RAM:     {mem.percent}% (usable {mem.available // (1024*1024)} MB)\n"
        f"💾 Disk:    {disk.percent}% ({disk.used // (1024*1024*1024)}GB/{disk.total // (1024*1024*1024)}GB)\n"
        f"🌐 Network: {net_text}\n"
        f"⏱️ Uptime:  {str(uptime).split('.')[0]}\n"
        f"```"
    )

    await ctx.channel.send(text)

# --- !docker ps: Show all container Docker are running ---
async def docker_ps(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.channel.send(f"⛔️You are not allowed to use this command.")
    await ctx.channel.send(f"🐳 Checking container...")
    try:
        output = subprocess.run('docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Size}}"', capture_output=True, text=True, check=True, shell=True)
        msg = output.stdout
        if not msg:
            msg = "(No container is running.)"
        await send_long_sys_message(ctx.channel, msg)
    except subprocess.CalledProcessError as e:
        await send_long_sys_message(ctx.channel, "Error occurred while checking container" + e.stdout)

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


async def get_network_speed():
    url = "http://update-manager:20000/network-speed"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['upload_kb'], data['download_kb']
    except Exception:
        return None, None