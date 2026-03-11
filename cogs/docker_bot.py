import os
import discord
import docker
import asyncio
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))

from cogs.utils.dropdown_bar import DropdownBar
from cogs.utils.notification_msg import NotificationMsg

class DockerBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.client = docker.from_env()
            
        except Exception as e:
            print(f"Error initializing Docker client: {e}")
            self.client = None

    async def handle_docker_action(self, container_name, action_type):
        """
        Logic callback passed to the DropdownBar.
        Handles Restart and Stop actions.
        """
        try:
            container = self.client.containers.get(container_name)
            
            if action_type == "Restart":
                container.restart()
                verb = "restarted"
                
            elif action_type == "Stop":
                container.stop()
                verb = "stopped"
                
            else:
                return False, NotificationMsg.error_msg(title="Error", description="Unknown action")

            embed = NotificationMsg.success_msg(
                title=f"Container {action_type}ed",
                description=f"Successfully **{verb}** container `{container_name}`."
            )
            
            return verb, embed

        except docker.errors.NotFound:
            return False, NotificationMsg.error_msg(title="Not Found", description="Container deleted.")
        
        except Exception as e:
            return False, NotificationMsg.error_msg(title="System Error", description=str(e))

    @app_commands.command(name="docker", description="Manage Docker containers on the San Jose node")
    async def docker_manage(self, interaction: discord.Interaction):
        # 1. Admin Check
        if interaction.user.id != ADMIN_ID:
            embed = NotificationMsg.error_msg(
                title="Permission Denied",
                description="You don't have permission to manage Docker containers."
            )
            
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # 2. Docker Client Check
        if not self.client:
            return await interaction.response.send_message("Docker Engine unreachable.", ephemeral=True)

        # 3. Get Containers
        containers = self.client.containers.list(all=True)
        if not containers:
            return await interaction.response.send_message("No containers available.", ephemeral=True)

        # 4. Define Actions for the Template
        # Format: "Label": (callback_function, button_style)
        action_map = {
            "Restart": (self.handle_docker_action, discord.ButtonStyle.primary),
            "Stop": (self.handle_docker_action, discord.ButtonStyle.danger)
        }
        
        # 5. Initialize Universal View
        # monitored_containers is empty set here since this is just management, not auto-heal
        view = DropdownBar(
            containers,
            self.client,
            set(), # Empty set for 'active_items' since we are using Restart/Stop
            action_map,
            mode="docker"
        )
        
        await interaction.response.send_message("🐳 **Docker Manager**", view=view, ephemeral=True)

        view.message = await interaction.original_response()

async def setup(bot):
    await bot.add_cog(DockerBot(bot))