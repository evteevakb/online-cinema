"""
PostgreSQL fixtures.
"""

from typing import Dict, List

import pytest_asyncio
from settings import PostgreSettings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine,
)
from sqlalchemy.pool import NullPool

from models.entity import Base

db_settings = PostgreSettings()

dsn_async = (
    f"postgresql+asyncpg://{db_settings.user}:{db_settings.password}"
    f"@{db_settings.host}:{db_settings.port}/{db_settings.db}"
)

engine = create_async_engine(
    dsn_async,
    echo=False,
    future=True,
    pool_pre_ping=True,
    poolclass=NullPool,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with async_session_factory() as session:
        yield session


@pytest_asyncio.fixture(name="pg_write_data")
async def pg_write_data(db_session: AsyncSession):
    """Фикстура для записи данных."""

    async def inner(model, values: List[Dict]):
        try:
            instances = [model(**item) for item in values]
            db_session.add_all(instances)
            await db_session.commit()
            print(f"Successfully committed {len(instances)} instances")
        except Exception as e:
            await db_session.rollback()
            print(f"Error while committing: {e}")
            raise e

    return inner


@pytest_asyncio.fixture(autouse=True)
async def clean_tables(db_session: AsyncSession):
    yield
    try:
        await db_session.execute(
            text("TRUNCATE TABLE auth.users, auth.login_history CASCADE")
        )
        await db_session.commit()
    except Exception as e:
        await db_session.rollback()
        raise e


@pytest_asyncio.fixture(autouse=True)
async def refresh_db():
    """Полный рефреш базы: drop + create."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
