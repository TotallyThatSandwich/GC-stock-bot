from discord.ext import commands
from discord import app_commands, Interaction
from db.modules import Stock  # adjust if your path differs


class StockPrices(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stock_prices", description="List all available stocks and their prices.")
    async def stock_prices(self, ctx):
        stocks = await Stock.all().order_by("-price")

        if not stocks:
            await ctx.response.send_message("No stocks are currently available.", ephemeral=True)
            return

        lines = []
        for stock in stocks:
            lines.append(f"**{stock.ticker}**: ${stock.price:.2f} ({stock.market_shares_available} available)")

        message = "**Current Stock Prices**\n\n" + "\n".join(lines)
        await ctx.response.send_message(message)


async def setup(bot):
    await bot.add_cog(StockPrices(bot))

