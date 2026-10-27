from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    url=settings.postgres_url,
    echo=True,
    pool_size=20,
    max_overflow=10,
    pool_timeout=10,
    pool_recycle=1800,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession, 
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session