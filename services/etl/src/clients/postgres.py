"""
Provides functionality for connecting to a PostgreSQL instance.
"""

from contextlib import closing
import logging
from typing import Any

import psycopg
from pydantic_settings import BaseSettings

from utils.backoff import backoff


class PostgreSettings(BaseSettings):
    """Configuration settings for connecting to a PostgreSQL instance."""

    db: str
    user: str
    password: str
    host: str
    port: int

    class Config:
        env_prefix = "POSTGRES_"


class PostgresClient:
    def __init__(
        self,
        settings: PostgreSettings = PostgreSettings(),
        logger: logging.Logger = logging.getLogger(__name__),
    ) -> None:
        self.dsl = {
            "dbname": settings.db,
            "user": settings.user,
            "password": settings.password,
            "host": settings.host,
            "port": settings.port,
        }
        self.logger = logger

    @backoff(
        min_delay_sec=2,
        max_delay_sec=70,
        max_retries=5,
        factor=2,
        retry_exceptions=[
            psycopg.Error,
        ],
    )
    def get_data(
        self,
        connection: psycopg.connection,
        query: str,
        params: dict[str, Any],
    ) -> Any:
        """Executes a parameterized SQL query and returns results.

        Args:
            connection: active PostgreSQL database connection;
            query: SQL query to execute;
            params: parameters to use with the query.

        Returns:
            Query results as dictionaries mapping column names to values.
        """
        with closing(connection.cursor()) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
