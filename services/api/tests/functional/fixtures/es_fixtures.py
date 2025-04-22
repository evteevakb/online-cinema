"""
Elasticsearch fixtures for functional tests.
"""

from pathlib import Path
from typing import Any, AsyncGenerator, Awaitable, Callable

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
import pytest_asyncio

from settings import ElasticSettings
from testdata.es_mappings import ElasticMappings


es_settings = ElasticSettings()
ElasticMappings.load_all(Path("./schemas/"))


@pytest_asyncio.fixture(name="es_client", scope="session")
async def es_client() -> AsyncGenerator[AsyncElasticsearch, None]:
    """Provides a shared asynchronous Elasticsearch client for the session.

    Yields:
        AsyncElasticsearch: an Elasticsearch client instance.
    """
    es_client = AsyncElasticsearch(
        hosts=[f"http://{es_settings.host}:{es_settings.port}"],
        basic_auth=(es_settings.user, es_settings.password),
    )
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name="es_delete_index")
def es_delete_index(
    es_client: AsyncElasticsearch,
) -> Callable[[str], Awaitable[None]]:
    """Fixture to delete an Elasticsearch index if it exists.

    Args:
        es_client (AsyncElasticsearch): Elasticsearch client instance.

    Returns:
        Callable: async function to delete an index by name.
    """

    async def inner(index: str):
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index=index)

    return inner


@pytest_asyncio.fixture(name="es_write_data")
def es_write_data(
    es_client: AsyncElasticsearch,
    es_delete_index: Callable[[str], Awaitable[None]],
) -> Callable[[str, list[dict[str, Any]]], Awaitable[None]]:
    """Fixture to write data to an Elasticsearch index with mappings and bulk insert.

    Args:
        es_client (AsyncElasticsearch): Elasticsearch client instance.
        es_delete_index (Callable): function to clear the index before writing.

    Returns:
        Callable: async function to write test data to the index.
    """

    async def inner(index: str, es_data: list[dict[str, Any]]) -> None:
        await es_delete_index(index)
        mapping = ElasticMappings.get(index)
        await es_client.indices.create(index=index, body=mapping.to_dict())

        bulk_query: list[dict] = []
        for row in es_data:
            data = {"_index": index, "_id": row["id"]}
            data.update({"_source": row})
            bulk_query.append(data)

        _, errors = await async_bulk(
            client=es_client,
            actions=bulk_query,
            refresh="wait_for",
        )

        await es_client.close()

        if errors:
            raise Exception("Error writing data to Elasticsearch")

    return inner
