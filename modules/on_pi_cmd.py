# modules/on_pi_cmd.py
import datetime
import logging
import os
import subprocess
import sys
import discord
import psutil

from discord.ext import commands
from dotenv import load_dotenv

ALLOWED_USER_IDS = [377676460334514176]

# --- Setup bot ---
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

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
        output = subprocess.check_output(['docker ps'], shell=True, text=True)
        msg = output.strip()
        if not msg:
            msg = "(No container is running.)"
        await ctx.channel.send(f"```bash\n{msg}\n```")
    except Exception as e:
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
    await ctx.send("Pulling latest code & rebuilding Docker...")
    result_pull = pull_latest_code()
    result_docker = rebuild_and_restart_docker()
    await ctx.send(f"✅ Pull result:\n```{result_pull}```")
    await ctx.send(f"🐳 Docker result:\n```{result_docker}```")

async def pull_latest_code(repo_path="/homelab/bots/discord-bot"):
    try:
        # Go to direction and pull
        result = subprocess.check_output(
            f"cd {repo_path} && git pull",
            shell=True, text=True
        )
        await result
    except subprocess.CalledProcessError as e:
        await f"Error pulling code:\n{e.output}"

async def rebuild_and_restart_docker(repo_path="/homelab/bots/discord-bot"):
    try:
        cmds = [
            f"cd {repo_path}",
            "docker stop the-herta || true",
            "docker rm herta || true",
            "docker build -t herta-bot .",
            "docker run -d --name herta --restart always --env-file .env discord-bot"
        ]
        result = subprocess.check_output(" && ".join(cmds), shell=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        return f"Error rebuilding:\n{e.output}"