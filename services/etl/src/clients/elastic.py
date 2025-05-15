"""
Provides functionality for connecting to a Elasticsearch instance.
"""

import json
import logging
from types import TracebackType

from elasticsearch import Elasticsearch
from pydantic_settings import BaseSettings


class ElasticSettings(BaseSettings):
    """Configuration settings for connecting to a Elasticsearch instance."""

    user: str
    password: str
    host: str
    api_port: int = 9200

    class Config:
        env_prefix = "ELASTIC_"


class ElasticClient:
    connection_error_message = (
        "ELASTICSEARCH: Client not connected to Elasticsearch cluster"
    )

    def __init__(
        self,
        settings: ElasticSettings = ElasticSettings(),
        logger: logging.Logger = logging.getLogger(__name__),
    ) -> None:
        self.client = None
        self.settings = settings
        self.logger = logger

    def __enter__(self) -> Elasticsearch:
        """Establishes connection to Elasticsearch cluster when entering context.

        Returns:
            Elasticsearch: the connected Elasticsearch client instance.
        """
        self.client = Elasticsearch(
            f"http://{self.settings.host}:{self.settings.api_port}",
            basic_auth=(self.settings.user, self.settings.password),
        )
        self.logger.debug("ELASTICSEARCH: Connection was established")
        return self.client

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Closes connection to Elasticsearch when exiting context.

        Args:
            exc_type: exception type if any exception occurred in the context;
            exc_value: exception value if any exception occurred in the context;
            traceback: traceback if any exception occurred in the context.
        """
        if self.client:
            self.client.close()
            self.logger.debug("ELASTICSEARCH: Connection was closed")
            if exc_type is not None:
                self.logger.error(
                    "ELASTICSEARCH: Exception occured: %s: %s. Traceback:\n %s",
                    exc_type,
                    exc_value,
                    traceback,
                )

    def is_index_exist(
        self,
        index_name: str,
    ) -> bool:
        """Checks if an index exists in the Elasticsearch cluster.

        Args:
            index_name: name of the index to check for existence.

        Returns:
            bool: True if the index exists, False otherwise.

        Raises:
            TypeError: if client does not have connection with Elasticsearch service.
        """
        if self.client is not None:
            return self.client.indices.exists(index=index_name)
        self.logger.error(self.connection_error_message)
        raise TypeError(self.connection_error_message)

    def create_index(
        self,
        index_name: str,
        schema_json_filepath: str,
    ) -> None:
        """Creates a new index in Elasticsearch using the specified schema.

        Args:
            index_name: name of the index to create;
            schema_json_filepath: path to JSON file containing index schema definition.

        Raises:
            TypeError: if client does not have connection with Elasticsearch service.
        """
        if self.client is not None:
            with open(schema_json_filepath, "r") as file:
                schema = json.load(file)
            _ = self.client.indices.create(
                index=index_name,
                body=schema,
            )
            self.logger.info(
                "ELASTICSEARCH: Index %s was successfully created", index_name
            )
        else:
            self.logger.error(self.connection_error_message)
            raise TypeError(self.connection_error_message)
