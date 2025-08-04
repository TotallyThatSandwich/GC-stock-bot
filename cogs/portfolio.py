import discord
from discord.ext import commands
from discord import app_commands

from db import User, Holding
from tortoise.exceptions import DoesNotExist
from decimal import Decimal
from core import get_or_create_user  # use core logic

class Trading(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="portfolio", description="WIP")
    async def portfolio(self, ctx):
        try:
            user = await get_or_create_user(ctx.user.id)
            await user.fetch_related("holdings__stock")
        except DoesNotExist:
            await ctx.response.send_message("User not found.")
            return

        if not user.holdings:
            await ctx.response.send_message("You don't own any stocks.")
            return

        embed = discord.Embed(title=f"{ctx.user.name}'s Portfolio", color=discord.Color.gold())
        total_value = Decimal("0")

        for holding in user.holdings:
            if holding.quantity == 0:
                return
            value = Decimal(holding.quantity) * Decimal(holding.stock.price)
            total_value += value
            embed.add_field(
                name=holding.stock.ticker,
                value=f"{holding.quantity} shares — ${value:.2f}",
                inline=False
            )

        embed.set_footer(
            text=f"Cash: ${user.balance:.2f} | Total Net Worth: ${Decimal(user.balance) + Decimal(total_value):.2f}"
        )
        await ctx.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Trading(bot))

