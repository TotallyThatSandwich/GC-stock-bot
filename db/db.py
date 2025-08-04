# db.py
from tortoise import Tortoise, run_async
import settings as settings

async def init_db():
    await Tortoise.init(
        db_url=settings.DB,
        modules={'models': ['db.modules']}  # Adjust if your models are elsewhere
    )
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()

