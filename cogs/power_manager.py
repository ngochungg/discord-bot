import os
import subprocess
import discord
from discord import app_commands
from discord.ext import commands, tasks
from cogs.utils.notification_msg import NotificationMsg
from wakeonlan import send_magic_packet

class PowerManager(commands.Cog):
    def __init__(self, bot):
      self.bot = bot
      self.lab_ip = os.getenv("LAB_IP")
      self.mac = os.getenv("LAB_MAC")
      self.channel_id = int(os.getenv("NOTIFICATION_CHANNEL_ID"), 0)
      self.is_online = True
      self.health_check.start()
      
    def cog_unload(self):
        self.health_check.cancel()
        
    def ping_host(self):
        # -c 1 for one packet, -W 1 for 1 second timeout
        try:
            output = subprocess.run(["ping", "-c", "1", "-W", "1", self.lab_ip], capture_output=True)
            return output.returncode == 0
        
        except Exception:
            return False
        
    @tasks.loop(seconds=60)
    async def health_check(self):
        currently_online = self.ping_host()
        
        if self.is_online and not currently_online:
            channel = self.bot.get_channel(self.channel_id)
            embed = NotificationMsg.error_msg(
                title="🚨 Critical Alert", 
                description=f"Homelab ({self.lab_ip}) is OFFLINE!"
            )
            await channel.send(embed=embed)
            for guild in self.guilds:
                if guild.system_channel:

                    await guild.system_channel.send(embed)
            
        self.is_online = currently_online
        
    @app_commands.command(name="wake_up", description="Wake up homelab on the San Jose node")
    async def wake_up(self, interaction: discord.Interaction):
        send_magic_packet(self.mac)
        
        embed = NotificationMsg.success_msg(
            title="WOL Sent",
            description=f"Sent WOL signal to {self.mac}. Homelab should be booting..."
        )
        await interaction.response.send_message(embed=embed)
    
async def setup(bot):
    await bot.add_cog(PowerManager(bot))