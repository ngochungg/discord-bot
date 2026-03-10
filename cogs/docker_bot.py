import discord
from discord import app_commands
from discord.ext import commands
import docker

from cogs.utils.notification_msg import NotificationMsg

class DockerBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.client = docker.from_env()

        except Exception as e:
            print(f"Error initializing Docker client: {e}")
            self.client = None

    @app_commands.command(name="docker", description="Manage Docker containers on the San Jose node")
    async def docker_manage(self, interaction: discord.Interaction):

        # Take a list of all containers and their statuses using the Docker SDK for Python
        containers = self.client.containers.list(all=True)

        if not containers:
            msg = NotificationMsg.error_msg(
                title="❌ No Containers Found",
                description="There are no Docker containers available to manage on the San Jose node."
            )
            await interaction.response.send_message(embed=msg, ephemeral=True)
            return
        
        # Create a view with a select menu to choose a container and buttons to manage it
        view = DockerManagerView(containers, self.client)
        await interaction.response.send_message("Select a container to manage:", view=view, ephemeral=True)

class DockerSelect(discord.ui.Select):
    def __init__(self, containers):
        options = [
            discord.SelectOption(
                label=c.name, 
                description=f"Status: {c.status}", 
                emoji="🐳" if c.status == "running" else "🔴"
            ) for c in containers
        ]
        super().__init__(
            placeholder="Select a container...", 
            options=options,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        # Set the selected container in the view so that the buttons can access it
        selected_value = self.values[0]
        self.view.selected_container = selected_value

        # Update the select menu options to show which container is currently selected
        for option in self.options:
            if option.label == selected_value:
                option.default = True
            else:
                option.default = False

        if len(self.view.children) == 2:
            # Restart button to restart the selected container
            restart_btn = discord.ui.Button(
                label="Restart", 
                style=discord.ButtonStyle.primary, 
                row=1
            )
            restart_btn.callback = self.view.restart_callback

            # Stop button to stop the selected container
            stop_btn = discord.ui.Button(
                label="Stop", 
                style=discord.ButtonStyle.danger, 
                row=1
            )
            stop_btn.callback = self.view.stop_callback
            
            # Add the restart button to the view
            self.view.add_item(restart_btn)
            # Add the stop button to the view
            self.view.add_item(stop_btn)

        await interaction.response.edit_message(
            content=f"Selected container: **{self.values[0]}**. Use the buttons below to manage it.",
            view=self.view
        )

class DockerManagerView(discord.ui.View):
    def __init__(self, containers, docker_client):
        super().__init__(timeout = None)
        self.selected_container = None
        self.docker_client = docker_client

        # Select menu to choose a container
        self.add_item(DockerSelect(containers))

        # Add exit button to the view that will allow the user to exit the management interface
        exit_btn = discord.ui.Button(
            label="Exit",
            style=discord.ButtonStyle.secondary,
            row=1
        )
        exit_btn.callback = self.exit_callback
        self.add_item(exit_btn)

    async def _handle_container_action(self, interaction: discord.Interaction, action: str):
        await interaction.response.defer(ephemeral=True)

        try:
            container = self.docker_client.containers.get(self.selected_container)

            if action == "restart":
                container.restart()
                action_verb = "restarted"
            elif action == "stop":
                container.stop()
                action_verb = "stopped"
            else:
                raise ValueError("Invalid action")
            
            # After performing the action, refresh the container list and update the select menu options to reflect any changes in container statuses
            new_containers = self.docker_client.containers.list(all=True)

            for item in self.children:
                if isinstance(item, DockerSelect):
                    item.options = [
                        discord.SelectOption(
                            label=c.name,
                            description=f"Status: {c.status}",
                            emoji="🐳" if c.status == "running" else "🔴",
                            default=False
                        ) for c in new_containers
                    ]

            selected_name = self.selected_container
            self.selected_container = None

            msg = NotificationMsg.success_msg(
                title=f"✅ Container {action.capitalize()}ed",
                description=f"Successfully performed **{action}** on `{selected_name}`. List updated."
            )
            
            await interaction.edit_original_response(
                content="Select a container to manage:",
                embed=msg, 
                view=self 
            )

        except docker.errors.NotFound:
            msg = NotificationMsg.error_msg(
                title="🚨 Container Not Found",
                description=f"Container '{self.selected_container}' does not exist."
            )
            await interaction.response.followup.send(embed=msg, ephemeral=True)

        except Exception as e:
            msg = NotificationMsg.error_msg(
                title=f"🚨 Error {action.capitalize()}ing Container",
                description=f"An error occurred while trying to {action} container '{self.selected_container}': {e}"
            )
            await interaction.response.followup.send(embed=msg, ephemeral=True)

    # Callbacks for the restart and stop buttons that call the _handle_container_action method with the appropriate action
    async def restart_callback(self, interaction: discord.Interaction):
        await self._handle_container_action(interaction, "restart")
    
    async def stop_callback(self, interaction: discord.Interaction):
        await self._handle_container_action(interaction, "stop")
    
    async def exit_callback(self, interaction: discord.Interaction):
        self.clear_items()
        self.stop()

        msg = NotificationMsg.info_msg(
            title="🔒 Session Closed",
            description="Docker management interface has been disabled and removed."
        )
        await interaction.response.edit_message(
            content=None,
            embed=msg,
            view=None
        )

    # async def restart_callback(self, interaction: discord.Interaction):
    #     await interaction.response.defer(ephemeral=True)

    #     # Try to restart the specified container and send an appropriate message based on the outcome
    #     try:
    #         # Get the container object using the Docker SDK for Python and restart it
    #         container = self.docker_client.containers.get(self.selected_container)
    #         container.restart()

    #         for item in self.children:
    #             if isinstance(item, discord.ui.Select):
    #                 for option in item.options:
    #                     option.default = False

    #         self.selected_container = None

    #         # Send a success message if the container was restarted successfully
    #         msg = NotificationMsg.success_msg(
    #             title = "✅ Container Restarted",
    #             description = f"Task complete! The menu has been reset."
    #         )
    #         await interaction.edit_original_response(
    #             content="Select a container to manage:",
    #             embed=msg, 
    #             view=self 
    #         )

    #     except docker.errors.NotFound:
    #         msg = NotificationMsg.error_msg(
    #             title = "🚨 Container Not Found",
    #             description = f"Container '{self.selected_container}' does not exist."
    #         )
    #         await interaction.response.followup.send(embed=msg, ephemeral=True)

    #     except Exception as e:
    #         msg = NotificationMsg.error_msg(
    #             title = "🚨 Error Restarting Container",
    #             description = f"An error occurred while restarting container '{self.selected_container}': {e}",
    #             view = self
    #         )
    #         await interaction.response.followup.send(embed=e, ephemeral=True)

        

async def setup(bot):
    await bot.add_cog(DockerBot(bot))