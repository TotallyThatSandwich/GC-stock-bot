from tortoise.exceptions import DoesNotExist
from db import User, Holding, Stock
from .market import generate_ticker
from decimal import Decimal

# Check if user exits or create user
async def get_or_create_user(discord_id: int) -> User:
    user, _ = await User.get_or_create(discord_id=discord_id)
    return user

# Get ballance of user
async def get_user_balance(discord_id: int) -> float:
    user = await get_or_create_user(discord_id)
    return round(user.balance, 2)

# add or remove user money
async def update_user_balance(discord_id: int, amount: float):
    user = await get_or_create_user(discord_id)
    user.balance += Decimal(amount)
    await user.save()

# Get holdings of user
async def get_user_holdings(discord_id: int):
    user = await get_or_create_user(discord_id)
    return await Holding.filter(user=user).prefetch_related("stock")

# 
async def get_user_holding(discord_id: int, stock: Stock) -> Holding:
    user = await get_or_create_user(discord_id)
    return await Holding.get_or_none(user=user, stock=stock)


async def modify_user_holding(discord_id: int, stock: Stock, quantity: int):
    user = await get_or_create_user(discord_id)
    holding = await Holding.get_or_none(user=user, stock=stock)

    if holding:
        holding.quantity += quantity
        if holding.quantity <= 0:
            await holding.delete()
        else:
            await holding.save()
    elif quantity > 0:
        await Holding.create(user=user, stock=stock, quantity=quantity)


async def sync_users(bot):
    for guild in bot.guilds:
        async for member in guild.fetch_members(limit=None):
            if member.bot:
                continue  # Skip bots

            # Ensure user exists
            user, _ = await User.get_or_create(
                discord_id=member.id,
                defaults={
                    "name": member.name,
                    "balance": 1000,
                    "market_value": 0
                }
            )

            # Try to find an existing stock owned by the user
            stock_exists = await Stock.filter(owner=user).exists()
            if stock_exists:
                continue

            # Generate a unique ticker
            base_ticker = generate_ticker(member.name)
            ticker = base_ticker
            counter = 1
            while await Stock.filter(ticker=ticker).exists():
                suffix = str(counter)
                ticker = (base_ticker[:5 - len(suffix)] + suffix).upper()
                counter += 1

            # Create the stock
            await Stock.create(
                owner=user,
                ticker=ticker,
                price=10.0,
                total_shares=500,
                market_shares_available=500
            )
