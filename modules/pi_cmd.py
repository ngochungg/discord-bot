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

# --- Add-on(s) function field ---
# --- Get network speed ---
async def get_network_speed():
    url = "http://update-manager:20000/network-speed"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['upload_mbps'], data['download_mbps']
                else:
                    return None, None
    except Exception as e:
        print(f"Error fetching network speed: {e}")
        return None, None

# ---General command field ---
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
        net_text = f"❌Cannot get network speed. Try again later."
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

# --- !update: Git pull and restart bot ---
async def update(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.channel.send(f"⛔️You are not allowed to use this command.")

    await ctx.channel.send("📦 Pulling latest code & rebuilding bot...")

    try:
        response = requests.post("http://update-manager:20000/update")
        data = response.json()

        output = data.get("output", "No output")
        if response.status_code == 200:
            await send_long_sys_message(ctx.channel,f"\n\n{output}\n")
        else:
            await send_long_sys_message(ctx.channel, f"❌ Error: {output}")

    except subprocess.CalledProcessError as e:
        error_output = e.stderr or e.stdout or "Unknown error"
        await send_long_sys_message(
            ctx.channel,
            f"❌ Update failed (exit code {e.returncode}):\n{error_output}\n"
        )

# --- !minecraft_server: Start minecraft server ---
async def minecraft_server(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.channel.send(f"⛔️You are not allowed to use this command.")

    await ctx.channel.send(f"🌐 Starting minecraft server...")

    try:
        output = subprocess.run("docker start minecraft autostop", capture_output=True, text=True, check=True, shell=True)
        msg = output.stdout
        if not msg:
            msg = f"❌ Cannot start minecraft server."
        await send_long_sys_message(ctx.channel, msg)

    except subprocess.CalledProcessError as e:
        error_output = e.stderr or e.stdout or "Unknown error"
        await send_long_sys_message(
            ctx.channel,
            f"❌ Failed to start server (exit code {e.returncode}):\n{error_output}\n"
        )

# --- Docker command field ---
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

# --- !docker compose up <container_name> -d --build : Rebuild container ---
# --- !docker compose down <container_name> : Stop container ---

# --- System command field ---
# --- !homelab_ls: Show homelab dir