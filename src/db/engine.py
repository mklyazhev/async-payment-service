from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

from src.common.config import get_settings

engine = create_async_engine(
    url=get_settings().database_url,
    pool_size=get_settings().db_pool_size,
    max_overflow=0,
    pool_pre_ping=True
)
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
