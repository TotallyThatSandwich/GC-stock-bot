import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal

class Ping(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="ping bot")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)  # ms
        await interaction.response.send_message(f"Pong! 🏓 Latency is `{latency}ms`")

async def setup(bot):
    await bot.add_cog(Ping(bot))
