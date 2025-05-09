import os
import discord

from dotenv import load_dotenv
from modules.on_message import handle_message
from modules.sys_cmd import on_sys_cmd

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')

@client.event
async def on_message(message):
    await handle_message(message, client)
    await on_sys_cmd(message)

client.run(TOKEN)