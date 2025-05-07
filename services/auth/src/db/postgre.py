"""
PostgreSQL client setup.
"""

from typing import AsyncGenerator

from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
)
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
    echo=db_settings.echo,  # enable log output
)
SQLAlchemyInstrumentor().instrument(
    engine=engine.sync_engine,
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
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
