"""
PostgreSQL client setup.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from core.config import PostgreSettings


Base = declarative_base()

db_settings = PostgreSettings()
dsn_sync = (
    f"postgresql+psycopg2://{db_settings.user}:{db_settings.password}"
    + f"@{db_settings.host}:{db_settings.port}"
    + f"/{db_settings.db}"
)
dsn_async = (
    f"postgresql+asyncpg://{db_settings.user}:{db_settings.password}"
    + f"@{db_settings.host}:{db_settings.port}"
    + f"/{db_settings.db}"
)
engine = create_async_engine(
    dsn_async,
    echo=True,  # enable log output
)
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # don't expire objects after transaction commit
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yields an asynchronous PostgreSQL session.

    Yields:
        AsyncSession: an instance of the asynchronous session.
    """
    async with async_session() as session:
        yield session
