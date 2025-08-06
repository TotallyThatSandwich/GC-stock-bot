import discord
from discord.ext import commands
from discord import app_commands

from tortoise.expressions import Q
from tortoise.functions import Sum
from decimal import Decimal

from db import User, Holding

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Show top users by total net worth")
    async def leaderboard(self, ctx):
        # Fetch all users and prefetch their holdings and stock prices
        users = await User.all().prefetch_related("holdings__stock")

        leaderboard = []

        for user in users:
            total_value = Decimal(user.balance)
            for holding in user.holdings:
                total_value += Decimal(holding.quantity) * Decimal(holding.stock.price)

            leaderboard.append((user.name, total_value))

        # Sort descending by total net worth
        leaderboard.sort(key=lambda x: x[1], reverse=True)

        embed = discord.Embed(title="📈 Top Players", color=discord.Color.green())
        for i, (name, net_worth) in enumerate(leaderboard[:10], start=1):
            embed.add_field(
                name=f"{i}. {name} - ${net_worth:.2f}",
                value="",
                inline=False
            )

        await ctx.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))

