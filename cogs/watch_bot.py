import os
import json
import docker
import discord
from discord import app_commands
from discord.ext import commands, tasks

from cogs.utils.dropdown_bar import DropdownBar
from cogs.utils.notification_msg import NotificationMsg

CONFIG_PATH = "monitored_services.json"
ALERT_CHANNEL_ID = int(os.getenv("NOTIFICATION_CHANNEL_ID", 0))

class WatchBot(commands.Cog):
    def __init__(self, bot):
      self.bot = bot
      self.client = docker.from_env()
      self.monitored_containers = self.load_monitored_services()
      if self.monitored_containers is None:
          self.monitored_containers = set()
      self.auto_heal.start()
    
    def load_monitored_services(self):
        if os.path.exists(CONFIG_PATH):
            try:
                # Check if file is not empty before loading
                if os.path.getsize(CONFIG_PATH) > 0:
                    with open(CONFIG_PATH, "r") as f:
                        return set(json.load(f))
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Config file corrupted or empty. Resetting... Error: {e}")
                    
    def save_monitor_services(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(list(self.monitored_containers), f)
            
    async def callback_func(self, container_name):
        
        # Ensure it;s a sete before operating
        if self.monitored_containers is None:
            self.monitored_containers = set()
        
        # This function is passed to the View to andle data
        if container_name in self.monitored_containers:
            self.monitored_containers.remove(container_name)
            action = "Disabled"
            
        else:
            self.monitored_containers.add(container_name)
            action = "Enabled"
            
        self.save_monitor_services()
        return action
    
    def cog_unload(self):
        self.auto_heal.cancel()
        
    @tasks.loop(seconds=15)
    async def auto_heal(self):
        if not self.monitored_containers:
            return
        
        channel = self.bot.get_channel(ALERT_CHANNEL_ID)
        
        for name in list(self.monitored_containers):
            try:
                container = self.client.containers.get(name)
                
                # Check if container is not in the desired 'running'
                if container.status != "running":
                    
                    # Perform the restart first
                    container.restart()
                    
                    # Sync the local obj with Docker
                    container.reload()
                    
                    if channel:
                        embed = NotificationMsg.success_msg(
                            title=" Auto-Heal Executed",
                            description=f"Service `{name}` was down. It has been successfully restarted."
                        )
                    
                    else:
                        embed = NotificationMsg.error_msg(
                            title="🚨 Auto-Heal Failed",
                            description=f"Service `{name}` failed to recover. Current status: **{container.status}**."
                        )

                    await channel.send(embed=embed)          

            except docker.errors.NotFound:
                self.monitored_containers.remove(name)
                self.save_monitor_services()
                print(f"Removed {name} from tracking: Container not found.")
                    
            except Exception as e:
                print(f"Monitor error for {name}: {e}")
                
    @app_commands.command(name="tracking", description="Manage Docker auto-healing services")
    async def tracking(self, interaction: discord.Interaction):
        # Check admin here
        
        # List container
        containers = self.client.containers.list(all=True)
        view = DropdownBar(
            containers,
            self.client,
            self.monitored_containers,
            self.callback_func
        )
        await interaction.response.send_message("🛡️ **Service Monitoring Dashboard**", view=view, ephemeral=True)
        
async def setup(bot):
    await bot.add_cog(WatchBot(bot))