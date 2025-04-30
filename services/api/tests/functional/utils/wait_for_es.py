"""
Elasticsearch connection wait script.
"""

import logging

import backoff
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError

from settings import ElasticSettings


logger = logging.getLogger(__name__)
settings = ElasticSettings()


def is_es_available(
    es_client: Elasticsearch,
) -> bool:
    """Checks if the Elasticsearch instance is available.

    Args:
        es_client (Elasticsearch): an instance of the Elasticsearch client.

    Returns:
        bool: True if Elasticsearch responds to a ping, False otherwise.
    """
    return es_client.ping()


@backoff.on_exception(
    backoff.expo,
    ConnectionError,
    max_tries=5,
    jitter=backoff.random_jitter,
)
def wait_for_es(
    es_client: Elasticsearch,
) -> None:
    """Waits for Elasticsearch to become available using exponential backoff.

    Args:
        es_client (Elasticsearch): an instance of the Elasticsearch client.

    Raises:
        ConnectionError: if Elasticsearch is not available after retries.
    """
    if not is_es_available(es_client):
        logger.warning("Elasticsearch is not available.")
        raise ConnectionError("Elasticsearch is not available.")


if __name__ == "__main__":
    with Elasticsearch(
        hosts=f"http://{settings.host}:{settings.port}",
        basic_auth=(settings.user, settings.password),
    ) as es_client:
        wait_for_es(es_client)
