"""
Common fixtures for functional tests.
"""

from typing import Awaitable, Callable

import pytest_asyncio
from redis.asyncio import Redis


@pytest_asyncio.fixture(name="refresh")
def refresh(
    redis_client: Redis,
    es_delete_index: Callable[[str], Awaitable[None]],
) -> Callable[[str], Awaitable[None]]:
    """Fixture to clear both Redis and a given Elasticsearch index.

    Args:
        redis_client (Redis): Redis client instance.
        es_delete_index (Callable): function to delete the Elasticsearch index.

    Returns:
        Callable: async function to clear Redis and the specified Elasticsearch index.
    """

    async def inner(index: str):
        await es_delete_index(index)
        await redis_client.flushdb()

    return inner
