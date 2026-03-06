import discord
from discord import app_commands
from discord.ext import commands
import psutil
import platform
import datetime

class Monitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="status", description="Xem thông số Homelab tại San Jose")
    async def status(self, interaction: discord.Interaction):
        # Lấy thông số hệ thống
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        # disk = psutil.disk_usage('/')
        uname = platform.uname()
        
        # Tạo giao diện Embed đẹp mắt
        embed = discord.Embed(
            title="🖥️ Homelab System Status",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="🌐 OS", value=f"{uname.system} {uname.release}", inline=False)
        embed.add_field(name="🔥 CPU Usage", value=f"{cpu_usage}%", inline=True)
        embed.add_field(name="🧠 RAM", value=f"{ram.percent}% ({ram.used//1048576}MB / {ram.total//1048576}MB)", inline=True)
        
        for part in psutil.disk_partitions():
            if part.mountpoint == '/home' or part.mountpoint == '/srv' or part.mountpoint == '/hdd/storage':
                disk = psutil.disk_usage(part.mountpoint)
                embed.add_field(name="💾 Disk", value=f"{disk.percent}%", inline=True)
                break
        
        
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Monitor(bot))