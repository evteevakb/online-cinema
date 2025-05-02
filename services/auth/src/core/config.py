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


class PostgreSettings(BaseSettings):
    """Configuration settings for PostgreSQL database."""

    user: str
    password: str
    host: str
    port: int
    db: str

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
