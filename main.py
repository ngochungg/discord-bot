import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# 1. Load environment variables from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MY_GUILD_ID = os.getenv('MY_GUILD_ID')
ADMIN_ID = os.getenv('ADMIN_ID')  # Chuyển ADMIN_ID thành số nguyên

# 2. Create a bot instance with the specified command prefix and intents
class MyBot(commands.Bot):

    # 3. Initialize the bot with the necessary intents
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        
        # 4. Load the cogs (extensions) from the 'cogs' directory
        if os.path.exists('./cogs'):
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    try:
                        await self.load_extension(f'cogs.{filename[:-3]}')
                        print(f'✅ Loaded cog: {filename}')
                    except Exception as e:
                        print(f'❌ Failed to load cog: {filename}. Error: {e}')

        @self.tree.command(name="reload", description="Install module again (Admin only)")
        async def reload(interaction: discord.Interaction, extension: str):
            # Kiểm tra ID của bạn (Thay ADMIN_ID bằng ID thật của bạn)
            if interaction.user.id != ADMIN_ID:
                return await interaction.response.send_message("❌ You don't have permission to use this command!", ephemeral=True)
            
            try:
                await self.reload_extension(f'cogs.{extension}')
                await interaction.response.send_message(f"✅ Reloaded module: `{extension}`", ephemeral=True)
                print(f"🔄 Module {extension} has been reloaded.")
            except Exception as e:
                await interaction.response.send_message(f"❌ Error: `{e}`", ephemeral=True)

        await self.tree.sync()  # Sync the command tree with Discord
    
    # 5. Define the on_ready event to print a message when the bot is ready
    async def on_ready(self):
        print(f"✅ Bot {self.user} is online!")

        for guild in self.guilds:
            if guild.system_channel:
                await guild.system_channel.send(f"✅ Bot {self.user} is online!")
                print(f'📢 Sent notification to system channel of server: {guild.name}')

bot = MyBot()

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)