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


class OAuthSessionSettings(BaseSettings):
    """Configuration settings for OAuth session."""

    secret_key: str

    class Config:
        env_prefix = "OAUTH_SESSION_"


class OAuthBaseSettings(BaseSettings):
    """Configuration settings for base OAuth client."""

    client_id: str
    client_secret: str
    auth_uri: str
    token_uri: str
    redirect_uri: str


class OAuthGoogleSettings(OAuthBaseSettings):
    """Configuration settings for OAuth Google client."""

    auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    token_uri: str = "https://oauth2.googleapis.com/token"
    server_metadata_url: str = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )

    class Config:
        env_prefix = "OAUTH_GOOGLE_"


class YandexProviderSettings(BaseSettings):
    """Configuration settings for Yandex Provider."""

    client_id: str
    client_secret: str
    name: str = 'yandex'
    access_token_url: str = 'https://oauth.yandex.ru/token'
    authorize_url: str = 'https://oauth.yandex.ru/authorize'
    api_base_url: str = 'https://login.yandex.ru'

    class Config:
        env_prefix = "YANDEX_"
