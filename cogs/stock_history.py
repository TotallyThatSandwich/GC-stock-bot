import discord
from discord.ext import commands
from discord import app_commands

from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime, timedelta
from db import StockPriceHistory, Stock
from tortoise.exceptions import DoesNotExist

class StockHistory(commands.Cog):
    """
    A cog for generating and displaying stock price history graphs.
    """
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stock_history", description="Displays a graph of a stock's price history for the last 7 days.")
    @app_commands.guilds(discord.Object(id=1082280059018162186))
    async def stock_history(self, ctx: discord.Interaction, ticker: str):
        """
        Creates and sends a graph of a stock's 7-day price history.
        """
        await ctx.response.defer()

        try:
            stock = await Stock.get(ticker=ticker.upper())
        except DoesNotExist:
            await ctx.followup.send("Stock not found. Please check the ticker symbol.")
            return

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        prices = await StockPriceHistory.filter(stock=stock, timestamp__gte=start_date).order_by("timestamp")

        if not prices:
            await ctx.followup.send("No price history available for the last 7 days.")
            return

        # --- Graph Generation ---
        width, height = 800, 400
        left_padding = 100
        padding = 60
        image = Image.new("RGB", (width, height), "#23272A")
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 15)
            title_font = ImageFont.truetype("arial.ttf", 28)
        except IOError:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()

        values = [float(p.price) for p in prices]
        timestamps = [p.timestamp for p in prices]
        min_price, max_price = min(values), max(values)
        span = max_price - min_price
        
        y_buffer = span * 0.1
        y_min = min_price - y_buffer
        y_max = max_price + y_buffer
        y_span = y_max - y_min if y_max != y_min else 1
        y_min = max(0, y_min)
        if y_span == 0:
            y_span = y_max

        plot_width = width - left_padding - padding
        plot_height = height - 2 * padding

        points = []
        # Check if there is more than one data point to prevent ZeroDivisionError
        if len(timestamps) > 1:
            for p in prices:
                x = left_padding + (timestamps.index(p.timestamp) / (len(timestamps) - 1)) * plot_width
                y = height - padding - ((float(p.price) - y_min) / y_span) * plot_height
                points.append((x, y))
        else: # Handle the case of a single data point
            # Center the single point in the middle of the graph
            x = left_padding + plot_width / 2
            y = height - padding - ((float(prices[0].price) - y_min) / y_span) * plot_height
            points.append((x, y))

        if len(points) > 1:
            gradient_fill = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            gradient_draw = ImageDraw.Draw(gradient_fill)
            
            polygon_points = [(p[0], p[1]) for p in points]
            polygon_points.append((points[-1][0], height - padding))
            polygon_points.append((points[0][0], height - padding))

            gradient_draw.polygon(polygon_points, fill="#42f57277")

            alpha_mask = Image.new("L", (width, height), 0)
            alpha_draw = ImageDraw.Draw(alpha_mask)
            
            for y in range(height):
                alpha = int(255 * (1 - ((y - padding) / plot_height))) if y > padding and y < height - padding else 0
                alpha_draw.line((0, y, width, y), fill=alpha)
                
            gradient_fill.putalpha(alpha_mask)
            image.paste(gradient_fill, (0, 0), gradient_fill)

            draw.line(points, fill="#42f572", width=4, joint="curve")

        for x, y in points:
            draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill="#42f572", outline="#ffffff", width=2)
        
        # --- Draw Labels and Axes ---
        
        # Draw grid lines and labels for Y-axis
        num_y_labels = 5
        for i in range(num_y_labels):
            y = padding + i * (plot_height / (num_y_labels - 1))
            price_label = y_max - i * (y_span / (num_y_labels - 1))
            draw.line((left_padding, y, width - padding, y), fill="#4a4d52", width=1)
            draw.text((left_padding - 10, y), f"${price_label:.2f}", fill="#e3e3e3", font=font, anchor="ra")

        # Draw grid lines and labels for X-axis
        # This also needs to handle the case of a single data point
        num_x_labels = 7
        for i in range(num_x_labels):
            x = left_padding + i * (plot_width / (num_x_labels - 1))
            # Check for len(timestamps) > 1 before division
            if len(timestamps) > 1:
                date_label_index = round(i * (len(timestamps) - 1) / (num_x_labels - 1))
            else:
                date_label_index = 0 # If only one timestamp, use it
            
            date_label = timestamps[date_label_index].strftime("%b %d")
            draw.line((x, padding, x, height - padding), fill="#4a4d52", width=1)
            draw.text((x, height - padding + 10), date_label, fill="#e3e3e3", font=font, anchor="ma")
        
        # Draw axis lines on top
        draw.line((left_padding, padding, left_padding, height - padding), fill="#ffffff", width=2)
        draw.line((left_padding, height - padding, width - padding, height - padding), fill="#ffffff", width=2)

        # Title
        draw.text((width // 2, 20), f"{ticker.upper()} - 7 Day Price History", fill="#ffffff", font=title_font, anchor="mm")
        
        # Save to buffer
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        # Send file
        await ctx.followup.send(file=discord.File(fp=buffer, filename="stock_history.png"))

async def setup(bot):
    await bot.add_cog(StockHistory(bot))
