"""
Redis client setup.
"""

from opentelemetry.instrumentation.redis import RedisInstrumentor
from redis.asyncio import Redis

redis: Redis | None = None
RedisInstrumentor().instrument()


async def get_redis() -> Redis:
    """Returns the global Redis client instance.

    Returns:
        Redis: the global Redis client.
    """
    return redis
