import os
import discord
from discord import app_commands
from discord.ext import commands, tasks
import psutil
import platform
import datetime

from cogs.utils.alert_msg import Alert
from cogs.utils.get_bar import Bar

ALERT_CHANNEL_ID = os.getenv("NOTIFICATION_CHANNEL_ID", 0)

class MonitorBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_system_status.start()

    def cog_unload(self):
        self.check_system_status.cancel()

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
            f"```\n"
            f"Root (/)  : {str(disk.percent).rjust(5)}% | {Bar.get_bar(disk.percent)}\n"
            f"HDD 1TB   : {str(disk_sdb.percent).rjust(5)}% | {Bar.get_bar(disk_sdb.percent)}\n"
            f"HDD 3.6TB : {str(disk_sdc.percent).rjust(5)}% | {Bar.get_bar(disk_sdc.percent)}\n"
            f"```"
        )
        
        embed.add_field(name="🌐 OS", value=f"{uname.system} {uname.release}", inline=False)
        embed.add_field(name="🔥 CPU Usage", value=f"{cpu_usage}%", inline=True)
        embed.add_field(name="🧠 RAM", value=f"{ram.percent}% ({ram.used//1048576}MB / {ram.total//1048576}MB)", inline=True)
        embed.add_field(name="💾 Storage Status", value=storage_info, inline=False)
        
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)

    @tasks.loop(seconds=10)
    async def check_system_status(self):

        if not self.bot.is_ready():
            return
        
        checklists = []
        
        # Check if alert channel is available
        channel = self.bot.get_channel(int(ALERT_CHANNEL_ID))
        if not channel:
            print(f"Alert channel with ID {ALERT_CHANNEL_ID} not found.")
            return
        
        # 1. Check CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage > 90:
            embed = Alert.alert_msg(
                title="High CPU Usage",
                description=f"CPU usage is at {cpu_usage}%. Please check your system."
            )
            await channel.send(embed=embed)
        else:
            checklists.append(f"✅ CPU usage is at {cpu_usage}%.")

        # 2. Check RAM usage
        ram = psutil.virtual_memory()
        if ram.percent > 90:
            embed = Alert.alert_msg(
                title="High RAM Usage",
                description=f"RAM usage is at {ram.percent}%. Please check your system."
            )
            await channel.send(embed=embed)
        else:
            checklists.append(f"✅ RAM usage is at {ram.percent}%.")
        
        # 3. Check Disk usage
        disks = {
            "Root (/)": "/",
            # "HDD 1TB": "/data/disk-sdb1",
            # "HDD 3.6TB": "/data/disk-sdc1"
        }

        for disk_name, disk_path in disks.items():
            disk_usage = psutil.disk_usage(disk_path)
            if disk_usage.percent > 90:
                embed = Alert.alert_msg(
                    title=f"High Disk Usage ({disk_name})",
                    description=f"Disk usage for {disk_name} is at {disk_usage.percent}%. Please check your system."
                )
                await channel.send(embed=embed)
            else:
                checklists.append(f"✅ Disk usage for {disk_name} is at {disk_usage.percent}%.")
        
        # Send a summary message if there are alerts
        if len(checklists) > 0:
            summary = "\n".join(checklists)

            embed = Alert.success_msg(
                title="🖥️ System Status Checklist",
                description=summary
            )
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text="San Jose Node - Automatic Monitor")

            await channel.send(embed=embed)

    @check_system_status.before_loop
    async def before_check_system_status(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(MonitorBot(bot))