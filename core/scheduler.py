import asyncio
from .market import simulate_market_fluctuations
from tortoise import Tortoise
from db import Stock, init_db
from datetime import datetime
import settings


async def run_scheduled_tasks():
    while True:
        print(f"[{datetime.now()}] Running scheduled tasks...")

        try:
            await simulate_market_fluctuations()
        except Exception as e:
            print(f"Error during market simulation: {e}")

        await asyncio.sleep(120)  # Run tasks every 120 seconds


async def start_scheduler():
    asyncio.create_task(run_scheduled_tasks())

