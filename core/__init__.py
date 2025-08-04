# core/__init__.py

from .scheduler import start_scheduler
from .user import (
    get_or_create_user,
    get_user_balance,
    update_user_balance,
    get_user_holdings,
    get_user_holding,
    modify_user_holding,
    sync_users,
)
from .market import (
    buy_stock,
    sell_stock,
    adjust_stock_price,
    simulate_market_fluctuations,
    generate_ticker,
)

__all__ = [
    "start_scheduler",
    "get_or_create_user",
    "get_user_balance",
    "update_user_balance",
    "get_user_holdings",
    "get_user_holding",
    "modify_user_holding",
    "format_user_portfolio",
    "buy_stock",
    "sell_stock",
    "adjust_stock_price",
    "simulate_market_fluctuations",
    "sync_users",
    "generate_ticker",
]

