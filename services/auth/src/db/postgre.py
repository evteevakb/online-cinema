"""
PostgreSQL client setup.
"""

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from core.config import PostgreSettings


Base = declarative_base()

db_settings = PostgreSettings()
dsn = (
    f"postgresql+asyncpg://{db_settings.user}:{db_settings.password}"
    + f"@{db_settings.host}:{db_settings.port}"
    + f"/{db_settings.db}"
)
engine = create_async_engine(dsn, echo=True, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """Yields an asynchronous PostgreSQL session.

    Yields:
        AsyncSession: an instance of the asynchronous session.
    """
    async with async_session() as session:
        yield session
