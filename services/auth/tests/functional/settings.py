"""
Configuration settings for the auth test service.
"""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    """Configuration settings for the API."""

    project_name: str = "auth-service"
    container_name: str
    port: int
    auth_secret_key: str
    auth_algorithm: str
    auth_access_exp: int
    base_url: str | None = None

    model_config = ConfigDict(env_prefix="API_")

    def model_post_init(self, __context) -> None:
        """Post-initialization method to set the base URL."""
        if self.base_url is None:
            self.base_url = f"http://{self.container_name}:{self.port}/api/v1/"


class PostgreSettings(BaseSettings):
    """Configuration settings for PostgreSQL database."""

    user: str
    password: str
    host: str
    port: int
    db: str

    model_config = ConfigDict(env_prefix="POSTGRES_")


class RedisSettings(BaseSettings):
    """Configuration settings for Redis."""

    host: str
    port: int
    user_name: str
    user_password: str

    model_config = ConfigDict(env_prefix="REDIS_")
