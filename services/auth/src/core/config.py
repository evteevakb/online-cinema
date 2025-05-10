"""
Configuration settings for the auth service.
"""

from logging import config as logging_config
import os

from pydantic_settings import BaseSettings

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class APISettings(BaseSettings):
    """Configuration settings for the API."""

    port: int
    container_name: str
    project_name: str = "auth-service"
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    class Config:
        env_prefix = "API_"


class TracingSettings(BaseSettings):
    """Configuration settings for tracing service."""

    container_name: str
    port: int

    class Config:
        env_prefix = "TRACING_"


class PostgreSettings(BaseSettings):
    """Configuration settings for PostgreSQL database."""

    user: str
    password: str
    host: str
    port: int
    db: str
    echo: bool = False

    class Config:
        env_prefix = "POSTGRES_"


class RedisSettings(BaseSettings):
    """Configuration settings for Redis."""

    host: str
    port: int
    user_name: str
    user_password: str

    class Config:
        env_prefix = "REDIS_"


class RateLimiterSettings(BaseSettings):
    """Configuration settings for rate limiter."""

    times: int = 10
    seconds: int = 60

    class Config:
        env_prefix = "RATE_LIMIT_"
