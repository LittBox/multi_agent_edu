from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config.settings import settings




engine = create_async_engine(
    settings.database_url,
    echo=True,          # 打印 SQL 语句（开发环境）
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session



