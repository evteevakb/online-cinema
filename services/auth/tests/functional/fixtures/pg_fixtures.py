"""
PostgreSQL fixtures.
"""

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session
from sqlalchemy import insert, text
from settings import PostgreSettings
from models.entity import BaseModel
import pytest_asyncio
import asyncio
from typing import List, Dict


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
    echo=False,
    max_overflow=10,
    future=True
)
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)
AsyncScopedSession = async_scoped_session(
    async_session_factory,
    scopefunc=asyncio.current_task
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Фикстура с полной изоляцией для каждого теста"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        async with AsyncScopedSession(bind=conn) as session:
            try:
                yield session
            finally:
                await session.close()
                await engine.dispose()


@pytest_asyncio.fixture(name="pg_write_data")
async def pg_write_data(db_session: AsyncSession):
    """Фикстура для атомарной записи данных"""
    async def inner(model: BaseModel, values: List[Dict]):
        try:
            for item in values:
                instance = model(**item)
                db_session.add(instance)
            await db_session.commit()
            await db_session.close()
        except Exception as e:
            await db_session.rollback()
            raise e
    return inner


@pytest_asyncio.fixture(autouse=True)
async def clean_tables(db_session: AsyncSession):
    yield
    try:
        await db_session.execute(text("TRUNCATE TABLE auth.users, auth.login_history CASCADE"))
        await db_session.commit()
    except Exception as e:
        await db_session.rollback()
        raise e
