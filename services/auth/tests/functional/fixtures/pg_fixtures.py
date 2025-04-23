"""
PostgreSQL fixtures.
"""

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import insert
from settings import PostgreSettings
from auth.src.models.entity import BaseModel
import pytest_asyncio
from testdata.samples.users import user_sample
from typing import Awaitable, Callable, List, Dict, Any

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
engine = create_async_engine(dsn_async, echo=True, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """Yields an asynchronous PostgreSQL session.

    Yields:
        AsyncSession: an instance of the asynchronous session.
    """
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(name="pg_write_data")
async def pg_write_data() -> Callable[[BaseModel, List[Dict]], Awaitable[None]]:
    async def inner(model: BaseModel, value: List[Dict]) -> None:
        pg = get_session()
        await pg.execute(insert(model).values(value))
        await pg.commit()
    return inner
