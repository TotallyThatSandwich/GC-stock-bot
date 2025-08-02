# db.py
from tortoise import Tortoise, run_async

async def init_db():
    await Tortoise.init(
        db_url='',
        modules={'models': ['models']}  # Adjust if your models are elsewhere
    )
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()

