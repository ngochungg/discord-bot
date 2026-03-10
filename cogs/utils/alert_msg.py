from turtle import title

import discord

class Alert:
    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description

    @staticmethod
    def alert_msg(title: str, description: str) -> discord.Embed:
        # Tạo một Embed thực thụ
        embed = discord.Embed(
            title=f"🚨 {title}",
            description=f"```\n{description}\n```",
            color=discord.Color.red()
        )
        return embed
    
    @staticmethod
    def success_msg(title: str, description: str) -> discord.Embed:
        embed = discord.Embed(
            title=f"✅ {title}",
            description=f"```\n{description}\n```",
            color=discord.Color.green()
        )
        return embed