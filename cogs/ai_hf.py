import discord
from discord import app_commands
from discord.ext import commands
import os

class AIHuggingFace(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")

    @app_commands.command(name="ask_ai", description="Hỏi đáp với AI từ Hugging Face")
    async def ask_ai(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer() # Thông báo bot đang suy nghĩ
        # Phần gọi API sẽ code ở đây ở bước tiếp theo
        await interaction.followup.send(f"Bạn vừa hỏi: {prompt}. (Tính năng AI đang được thiết lập...)")

async def setup(bot):
    await bot.add_cog(AIHuggingFace(bot))