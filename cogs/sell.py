import discord
from discord.ext import commands
from discord import app_commands

from db import User
from tortoise.exceptions import DoesNotExist
from core import sell_stock, get_or_create_user 

class Sell(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sell", description="Sell stock at curent market price")
    async def sell_stock_cmd(self, ctx, ticker: str, amount: int):
        try:
            user = await get_or_create_user(ctx.user.id)
        except DoesNotExist:
            await ctx.response.send_message("User not found.", ephemeral=True)
            return

        try:
            response = await sell_stock(user, ticker, amount)
            await ctx.response.send_message(response)

        except ValueError as e:
            await ctx.response.send_message(f"Error: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Sell(bot))

