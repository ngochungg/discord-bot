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

# File in Pi path
PI_DIR = "/mnt/homelab"

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

# --- Find compose.yml file in homelab ---
def find_compose_file(service_name, base_dir=PI_DIR):
    for dir_name in os.listdir(base_dir):
        dir_path = os.path.join(base_dir, dir_name)
        compose_file = os.path.join(dir_path, "docker-compose.yml")

        if os.path.isfile(compose_file):
            with open(compose_file, "r") as f:
                if service_name in f.read():
                    return compose_file
    return None

# Run command compose with action up/down/restart
def run_compose_action(compose_path, service_name, action):
    return subprocess.run(
        ["docker", "compose", "-f", compose_path, action, "-d --build", service_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

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

    # Check container running or not
    check_mcserver = subprocess.run(
        'docker ps --filter "name=minecraft" --format "{{.Names}}"',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True  # Python 3.7+ để tự decode bytes -> str
    )

    output = check_mcserver.stdout.strip()

    if output:
        await ctx.channel.send(f"🌐 Minecraft server is already running!")
        return

    try:
        output = subprocess.run("docker start minecraft autostop", capture_output=True, text=True, check=True, shell=True)
        msg = output.stdout
        if not msg:
            msg = f"❌ Cannot start minecraft server."
        else:
            msg = f"✅ Minecraft server started."
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
        await send_long_sys_message(ctx.channel, f"❌ Error occurred while checking container" + e.stdout)

# --- !compose up/down/restart <service_name>: Rebuild container ---
async def compose(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.channel.send(f"⛔️You are not allowed to use this command.")

    # Get all message content
    content = ctx.content.strip()

    # Split it to array[]
    parts = content.split()

    if len(parts) < 3:
        await ctx.channel.send("⚠️ Please use command like this: `!compose <action> <service_name>`")
        return

    action = parts[1]  # 'up/down/restart'
    service_name = " ".join(parts[2:])  # 'service name', support long name

    # Call process function
    await start_compose_service(service_name, action, ctx)

# --- Processing function for !compose ---
async def start_compose_service(service_name, action, ctx):

    # Check action
    if action not in ["up", "down", "restart"]:
        await ctx.channel.send("⚠️ Invalid action! Please use: `up`, `down`, `restart`")
        return

    # Take path
    compose_path = find_compose_file(service_name)
    if not compose_path:
        await ctx.channel.send(f"❌ Service cannot found `{service_name}` in homelab.")
        return

    result = run_compose_action(compose_path, service_name, action)

    if result.returncode == 0:
        await ctx.channel.send(f"✅ `{action}` successfully for `{service_name}`.")
    else:
        await send_long_sys_message(ctx.channel,
            f"❌ Error occurs `{action}`:\n```\n{result.stderr.strip()}\n```"
        )

# --- System command field ---
# --- !homelab_ls: Show homelab dir
async def homelab_ls(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.channel.send(f"⛔️You are not allowed to use this command.")

    await ctx.channel.send(f"💾 Checking project...")
    output = subprocess.run('ls ' + PI_DIR, capture_output=True, text=True, check=True, shell=True)
    msg = output.stdout
    if not msg:
        msg = f"⚠️ Cannot find homelab project."

    await send_long_sys_message(ctx.channel, msg)