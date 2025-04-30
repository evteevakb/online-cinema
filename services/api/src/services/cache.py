"""
Module providing a cache interface.
"""

from abc import ABC, abstractmethod
import json
import logging
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import ConnectionError, TimeoutError


logger = logging.getLogger(__name__)


class BaseCache(ABC):
    """Abstract base class for a cache service."""

    @abstractmethod
    async def get(
        self,
        key: str,
    ) -> Any | None:
        """Retrieve the value associated with the given key from the cache.

        Args:
            key (str): the cache key to retrieve the value for.

        Returns:
            Any | None: the cached value if present, otherwise None.
        """
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        expire: int,
    ) -> None:
        """Store a value in the cache with a specified expiration time.

        Args:
            key (str): the cache key to store the value under.
            value (Any): the value to be stored in the cache.
            expire (int): expiration time in seconds.
        """
        pass


class RedisCache(BaseCache):
    """Redis cache implementation."""

    def __init__(
        self,
        redis_client: Redis,
    ) -> None:
        """Initialize the Redis cache instance.

        Args:
            redis_client (Redis): an instance of Redis client.
        """
        self.redis_client = redis_client

    async def get(
        self,
        key: str,
    ) -> Any | None:
        try:
            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except (ConnectionError, TimeoutError) as exc:
            logger.error(f"Redis connection failed: {exc}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: int,
    ) -> None:
        try:
            await self.redis_client.set(key, json.dumps(value), ex=expire)
        except (ConnectionError, TimeoutError) as exc:
            logger.error(f"Redis connection failed: {exc}")
