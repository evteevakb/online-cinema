"""
Provides functionality for connecting to a Redis instance.
"""

import logging

from pydantic_settings import BaseSettings

import redis


class RedisSettings(BaseSettings):
    """Configuration settings for connecting to a Redis instance."""

    host: str
    port: int
    user_name: str
    user_password: str

    class Config:
        env_prefix = "REDIS_"


class RedisClient:
    """Client for connecting to a Redis instance."""

    def __init__(
        self,
        settings: RedisSettings = RedisSettings(),
        logger: logging.Logger = logging.getLogger(__name__),
    ) -> None:
        self.client = redis.Redis(
            host=settings.host,
            port=settings.port,
            username=settings.user_name,
            password=settings.user_password,
        )
        self.logger = logger

    def is_connected(self) -> bool:
        """Checks if the Redis client is connected by sending a ping.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            self.client.ping()
            return True
        except redis.exceptions.RedisError as exc:
            self.logger.error(f"Failed to connect to Redis: {exc}")
            return False
