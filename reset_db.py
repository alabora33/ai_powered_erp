import asyncio
import logging
from backend.database import engine
from backend.models import Base

logging.basicConfig(level=logging.INFO)

async def reset():
    logging.info("Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logging.info("Recreating all tables with Universal Schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Database successfully reset and updated!")

if __name__ == "__main__":
    asyncio.run(reset())
