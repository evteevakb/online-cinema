"""
Redis fixtures for functional tests.
"""

from typing import AsyncGenerator

import pytest_asyncio
from redis.asyncio import Redis

from settings import RedisSettings

redis_settings = RedisSettings()


@pytest_asyncio.fixture(name="redis_client", scope="session")
async def redis_client() -> AsyncGenerator[Redis, None]:
    """Provides a shared asynchronous Redis client for the session.

    Yields:
        Redis: a Redis client instance.
    """
    redis_client = Redis(
        host=redis_settings.host,
        port=redis_settings.port,
        username=redis_settings.user_name,
        password=redis_settings.user_password,
    )
    yield redis_client
    await redis_client.aclose()
