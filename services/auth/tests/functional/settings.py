"""
Configuration settings for the auth service.
"""

import os
from logging import config as logging_config

from pydantic_settings import BaseSettings

from logger import LOGGING


logging_config.dictConfig(LOGGING)


class APISettings(BaseSettings):
    """Configuration settings for the API."""

    project_name: str = "auth-service"
    base_url: str | None = None
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
