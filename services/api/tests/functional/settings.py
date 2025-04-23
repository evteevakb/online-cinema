"""
Containes configuration utilities for API, Elasticsearch, and Redis services.
"""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    """Configuration settings for the API"""

    container_name: str
    port: int
    base_url: str | None = None

    model_config = ConfigDict(env_prefix="API_")

    def model_post_init(self, __context) -> None:
        """Post-initialization method to set the base URL."""
        if self.base_url is None:
            self.base_url = f"http://{self.container_name}:{self.port}/api/v1/"


class ElasticSettings(BaseSettings):
    """Configuration settings for the Elasticsearch"""

    host: str
    port: int
    user: str
    password: str

    model_config = ConfigDict(env_prefix="ELASTIC_")


class RedisSettings(BaseSettings):
    """Configuration settings for the Redis"""

    host: str
    port: int
    user_name: str
    user_password: str

    model_config = ConfigDict(env_prefix="REDIS_")
