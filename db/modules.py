# models.py
from tortoise import models, fields
import datetime

class User(models.Model):
    id = fields.IntField(pk=True)
    discord_id = fields.BigIntField(unique=True)
    name = fields.CharField(max_length=32)
    balance = fields.FloatField(default=500.0)
    market_cap = fields.FloatField(default=0.0)

    def __str__(self):
        return f"{self.name} ({self.discord_id})"

class Stock(models.Model):
    id = fields.IntField(pk=True)
    owner = fields.ForeignKeyField("models.User", related_name="issued_stock")
    ticker = fields.CharField(max_length=5, unique=True)
    price = fields.FloatField(default=10.0)
    total_shares = fields.IntField(default=500)
    market_shares_available = fields.IntField()  # how many shares are available in the market pool

    def __str__(self):
        return f"{self.ticker} @ {self.price}"

class Holding(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="holdings")
    stock = fields.ForeignKeyField("models.Stock", related_name="stock")
    quantity = fields.IntField()

class Trade(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="trades")
    stock = fields.ForeignKeyField("models.Stock", related_name="trades")
    quantity = fields.IntField()
    price = fields.FloatField()
    action = fields.CharField(max_length=4)  # "BUY" or "SELL"
    timestamp = fields.DatetimeField(auto_now_add=True)

class StockPriceHistory(models.Model):
    id = fields.IntField(pk=True)
    stock = fields.ForeignKeyField("models.Stock", related_name="price_history")
    timestamp = fields.DatetimeField(auto_now_add=True)
    price = fields.FloatField()

