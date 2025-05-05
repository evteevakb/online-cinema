"""
Provides functionality for loading data into Elasticsearch in batches.
"""

import logging
from typing import Any, Generator

from clients.elastic import ElasticClient
from elasticsearch.exceptions import ConnectionError, ConnectionTimeout
from utils.backoff import backoff

from elasticsearch import helpers


class ElasticLoader:
    """Loads data into Elasticsearch in batches and handles connection failures."""

    def __init__(
        self,
        index_name: str,
        schema_filepath: str,
        logger: logging.Logger = logging.getLogger(__name__),
    ) -> None:
        self.client = ElasticClient()
        self.index_name = index_name
        self.logger = logger
        with self.client:
            if not self.client.is_index_exist(self.index_name):
                self.client.create_index(
                    index_name=self.index_name,
                    schema_json_filepath=schema_filepath,
                )
                self.logger.info("ELASTICSEARCH: Index %s was created")

    def prepare_data(
        self, batch: list[dict[str, Any]]
    ) -> Generator[dict[str, Any], None, None]:
        """Prepares data for bulk loading into Elasticsearch.

        Args:
            batch: a list of dictionaries containing the data to load.

        Yields:
            A dictionary formatted for Elasticsearch bulk loading.
        """
        for row in batch:
            yield {
                "_index": self.index_name,
                "_id": row["id"],
                "_source": {
                    **row,
                },
            }

    @backoff(
        min_delay_sec=2,
        max_delay_sec=70,
        max_retries=5,
        factor=2,
        retry_exceptions=[
            ConnectionError,
            ConnectionTimeout,
        ],
    )
    def load(
        self,
        batch: list[dict[str, Any]],
    ) -> None:
        """Loads a batch of data into Elasticsearch with retry logic.

        Args:
            batch: a list of dictionaries containing the data to load.
        """
        self.logger.info(
            "ELASTICSEARCH: Start loading batch with length %s", len(batch)
        )
        with self.client as elastic_client:
            success, errors = helpers.bulk(elastic_client, self.prepare_data(batch))
            self.logger.info("ELASTICSEARCH: Loaded %s documents", success)
            if errors:
                self.logger.error(
                    "ELASTICSEARCH: During load the following errors occured: %s",
                    errors,
                )
