from db import User, Stock, Holding, Trade, StockPriceHistory
from tortoise.exceptions import DoesNotExist
from datetime import datetime
import random
from decimal import Decimal
import re


def generate_ticker(name: str) -> str:
    # Create a 5-character uppercase ticker from the username
    ticker = re.sub(r'[^A-Za-z]', '', name.upper())[:5]
    return ticker if ticker else "USERX"  # fallback if name is empty or only symbols

# Add holdings after purchase
async def get_or_create_holding(user: User, stock: Stock) -> Holding:
    holding, _ = await Holding.get_or_create(user=user, stock=stock, defaults={"quantity": 0})
    return holding

# Adjust price of stocks after purchase
async def adjust_stock_price(stock: Stock, direction: str, volume: int):
    adjustment_factor = 0.01


    if direction == "buy":
        stock.price *= (1 + adjustment_factor * volume)
    elif direction == "sell":
        stock.price *= (1 - adjustment_factor * volume)

    stock.price = max(stock.price, 0.01)
    await stock.save()

    await StockPriceHistory.create(stock=stock, price=stock.price)

# Purchase stock
async def buy_stock(buyer: User, ticker: str, quantity: int) -> str:
    try:
        stock = await Stock.get(ticker=ticker)
        price = stock.price
    except DoesNotExist:
        return f"Stock '{ticker}' does not exist."
    
    if quantity <= 0:
        return "You must buy at least one share."

    if stock.market_shares_available < quantity:
        return f"Only {stock.market_shares_available} shares available in the market."
    
    fee = 0.25
    total_price = (price * quantity) * (1 + fee)
    if buyer.balance < total_price:
        return f"Insufficient funds. You need ${total_price:.2f}."
    
    # Execute trade
    buyer.balance -= total_price
    stock.market_shares_available -= quantity
    holding = await get_or_create_holding(buyer, stock)
    holding.quantity += quantity

    await buyer.save()
    await stock.save()
    await holding.save()

    await adjust_stock_price(stock, direction="buy", volume=quantity)
    await Trade.create(user=buyer, stock=stock, quantity=quantity, price=price, action="BUY")

    return f"Bought {quantity} shares of {stock.ticker} for ${total_price:.2f}/${total_price/quantity:.2f} each."

# Sell stock
async def sell_stock(seller: User, ticker: str, quantity: int) -> str:

    try:
        stock = await Stock.get(ticker=ticker)
        price = stock.price
    except DoesNotExist:
        return f"Stock '{ticker}' does not exist."

    if quantity <= 0:
        return "You must sell at least one share."

    try:
        holding = await Holding.get(user=seller, stock=stock)
    except DoesNotExist:
        return f"You don’t own any shares of {stock.ticker}."

    if holding.quantity < quantity:
        return f"You only own {holding.quantity} shares of {stock.ticker}."

    total_value = price * quantity
    seller.balance += total_value
    holding.quantity -= quantity
    stock.market_shares_available += quantity

    await seller.save()
    await holding.save()
    await stock.save()

    await adjust_stock_price(stock, direction="sell", volume=quantity)
    await Trade.create(user=seller, stock=stock, quantity=quantity, price=price, action="SELL")

    return f"Sold {quantity} shares of {stock.ticker} for ${price * quantity:.2f}/${price:.2f} each."


async def simulate_market_fluctuations():
    stocks = await Stock.all()
    for stock in stocks:
        change = Decimal(random.uniform(-0.015, 0.025))  # -3% to +3%
        new_price = Decimal(stock.price) * (1 + change)
        stock.price = max(Decimal("0.01"), round(new_price, 2))
        await stock.save()

        # Optional: log to history
        await StockPriceHistory.create(stock=stock, price=stock.price)
