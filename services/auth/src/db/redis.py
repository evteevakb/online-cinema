"""
Redis client setup.
"""

from redis.asyncio import Redis


redis: Redis | None = None


async def get_redis() -> Redis:
    """Returns the global Redis client instance.

    Returns:
        Redis: the global Redis client.
    """
    return redis
