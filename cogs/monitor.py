import discord
from discord import app_commands
from discord.ext import commands
import psutil
import platform
import datetime

from cogs.utils.get_bar import get_bar

class Monitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="status", description="Xem thông số Homelab tại San Jose")
    async def status(self, interaction: discord.Interaction):
        # Take system metrics using psutil
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        uname = platform.uname()
        disk = psutil.disk_usage('/')
        disk_sdb = psutil.disk_usage('/data/disk-sdb1')
        disk_sdc = psutil.disk_usage('/data/disk-sdc1')
        
        # Create an embed message to display the system status
        embed = discord.Embed(
            title="🖥️ Homelab System Status",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        storage_info = (
            f"**Root (/)**:     `{disk.percent}%` | {get_bar(disk.percent)}\n"
            f"**HDD 1TB**:      `{disk_sdb.percent}%` | {get_bar(disk_sdb.percent)}\n"
            f"**HDD 3.6TB**:    `{disk_sdc.percent}%` | {get_bar(disk_sdc.percent)}"
        )
        
        embed.add_field(name="🌐 OS", value=f"{uname.system} {uname.release}", inline=False)
        embed.add_field(name="🔥 CPU Usage", value=f"{cpu_usage}%", inline=True)
        embed.add_field(name="🧠 RAM", value=f"{ram.percent}% ({ram.used//1048576}MB / {ram.total//1048576}MB)", inline=True)
        embed.add_field(name="💾 Storage Status", value=storage_info, inline=False)
        
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Monitor(bot))