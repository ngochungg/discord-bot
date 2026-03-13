import os
import subprocess
import discord
import time
from discord import app_commands
from discord.ext import commands, tasks
from cogs.utils.notification_msg import NotificationMsg
from wakeonlan import send_magic_packet

LAB_IP = os.getenv("LAB_IP")
NOTIFICATION_CHANNEL_ID = int(os.getenv("NOTIFICATION_CHANNEL_ID"), 0)

class PowerManager(commands.Cog):
    def __init__(self, bot):
      self.bot = bot
      self.lab_ip = LAB_IP
      self.channel_id = NOTIFICATION_CHANNEL_ID
      self.is_online = True
      self.health_check.start()

      self.restart_history = {}
      self.cool_down_locks = {}
      
    def cog_unload(self):
        self.health_check.cancel()
        
    def ping_host(self):
        # -c 1 for one packet, -W 1 for 1 second timeout
        try:
            output = subprocess.run(["ping", "-c", "10", "-W", "2", self.lab_ip], capture_output=True, stderr=subprocess.STDOUT)
            return True
        
        except (subprocess.CalledProcessError, Exception):
            return False

    def is_in_crash_loop(self, name):
        # Check if container restart over 3 times in 10 mins
        now = time.time()
        if name not in self.restart_history:
            self.restart_history[name] = []
            
        # Timestamp in 10mins (600s)
        self.restart_history[name] = [t for t in self.restart_history[name] if now - t < 600]
        
        return len(self.restart_history[name]) >= 3
        
    @tasks.loop(minutes=10)
    async def health_check(self):
        try:
            channel = self.bot.get_channel(self.channel_id) or await self.safe_fetch_channel()
            if not channel: return

            embed = None
            name = "homelab"
            now = time.time()

            if name not in self.cool_down_locks or now > self.cool_down_locks[name]:
                self.cool_down_locks[name] = now + 3600 # Lock auto-heal in 1 hour
                embed = NotificationMsg.error_msg(
                        title="CRITICAL: Crash-loop Detected",
                        description=f"Computer `{name}` restarted many times. \n**Auto-heal is stopped for 1 hour** to protect server."
                    )
                    
                # Send with View, Logs button
                await channel.send(embed=embed)
                embed = None

            currently_online = self.ping_host()
            await self.bot.wait_until_ready()

            if self.is_online and not currently_online:
                embed = NotificationMsg.error_msg(
                    title="🚨 Critical Alert", 
                    description=f"Homelab ({self.lab_ip}) is **OFFLINE**!"
                )

            if embed:
                await channel.send(embed=embed)

                for guild in self.bot.guilds:
                    if guild.system_channel:
                        try:
                            await guild.system_channel.send(embed=embed)
                        except:
                            continue

            self.is_online = currently_online
        
        except Exception as e:
            print(f"❌ Health Check Error: {e}")

    async def safe_fetch_channel(self):
        try:
            return await self.bot.fetch_channel(self.channel_id)
        except:
            return None

    @health_check.before_loop
    async def before_health_check(self):
        await self.bot.wait_until_ready()
        
    @app_commands.command(name="wake_up", description="Wake up homelab on the San Jose node")
    async def wake_up(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try :
            send_magic_packet(self.mac, ip_address=self.lab_ip, port=9)

            embed = NotificationMsg.success_msg(
                title="WOL Sent",
                description=f"Sent WOL signal to {self.mac}. Homelab should be booting..."
            )
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(content=f"Error: {e}")

async def setup(bot):
    await bot.add_cog(PowerManager(bot))
