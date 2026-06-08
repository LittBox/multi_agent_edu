import asyncio

from app.db.base import Base
from app.db.database import engine




async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(main())
