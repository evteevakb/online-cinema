import os
from logging import config as logging_config

from pydantic_settings import BaseSettings

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class APISettings(BaseSettings):

    auth_host: str
    auth_port: int
    project_name: str = "movies"
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    class Config:
        env_prefix = "API_"


class ElasticSettings(BaseSettings):
    host: str
    port: int
    user: str
    password: str

    class Config:
        env_prefix = "ELASTIC_"


class RedisSettings(BaseSettings):
    host: str
    port: int
    user_name: str
    user_password: str

    class Config:
        env_prefix = "REDIS_"
