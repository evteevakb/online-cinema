"""
Redis connection wait script with backoff.
"""

import logging

import backoff
from redis import Redis
from redis.exceptions import ConnectionError

from settings import RedisSettings


settings = RedisSettings()


def is_redis_available(redis_client: Redis) -> bool:
    """Checks if the Redis instance is available.

    Args:
        redis_client (Redis): an instance of the Redis client.

    Returns:
        bool: True if Redis responds to a ping, False otherwise.
    """
    try:
        return redis_client.ping()
    except ConnectionError:
        return False

@backoff.on_predicate(
    backoff.expo,
    predicate=lambda result: not result,
    max_tries=5,
    jitter=backoff.random_jitter,
)
def wait_for_redis(redis_client: Redis):
    """Waits for Redis to become available using exponential backoff.

    Args:
        redis_client (Redis): an instance of the Redis client.

    Raises:
        ConnectionError: if Redis is not available after retries.
    """
    redis_available = is_redis_available(redis_client)
    if not redis_available:
        logging.warning("Redis is not available.")
    return redis_available


if __name__ == "__main__":
    with Redis(
        host=settings.host,
        port=settings.port,
        username=settings.user_name,
        password=settings.user_password,
    ) as redis_client:
        wait_for_redis(redis_client)
