"""
Module providing a repository interface.
"""

from abc import ABC, abstractmethod
import logging
from typing import Any

from elastic_transport import ObjectApiResponse
from elasticsearch import AsyncElasticsearch, BadRequestError, NotFoundError

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """Abstract base class for a repository service."""

    @abstractmethod
    async def get_by_id(self, id: str | int, **kwargs: Any) -> dict[str, Any] | None:
        """Retrieve a single document by its ID.

        Args:
            id (str | int): Document identifier.
            **kwargs: Query options like `schema`, 'filter' etc.

        Returns:
            dict[str, Any] | None: Document data or None if not found.
        """
        pass

    @abstractmethod
    async def get_list(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Retrieve a list of documents using optional filters.

        Args:
            **kwargs: Query options like `body`, `from`, `size`, etc.

        Returns:
            list[dict[str, Any]]: List of matched documents.
        """
        pass


class ElasticsearchRepository(BaseRepository):
    """Elasticsearch repository implementation."""

    def __init__(self, elastic_client: AsyncElasticsearch) -> None:
        """Initialize the Elasticsearch repository instance.

        Args:
            elastic_client (AsyncElasticsearch): an instance of Elasticsearch client.
        """
        self.elastic_client = elastic_client

    async def get_by_id(self, id: str, **kwargs: Any) -> dict | None:
        """Retrieve a document from Elasticsearch by its ID.

        Args:
            id (str | int): Document identifier.
            **kwargs: Query options, must include 'index'.

        Returns:
            ObjectApiResponse[Any] | None: Document or None if not found.
        """
        index = kwargs.get("index")
        if not index:
            raise Exception("ElasticsearchRepository error: Index must be set")
        try:
            doc = await self.elastic_client.get(index=index, id=id)
            return doc.get("_source", {})
        except NotFoundError:
            return None

    async def get_list(self, **kwargs: Any) -> list[ObjectApiResponse[Any]]:
        """Retrieve documents using Elasticsearch search.

        Args:
            **kwargs: Passed directly to `Elasticsearch.search()`.

        Returns:
            list[ObjectApiResponse[Any]]: List of matching documents.
        """
        index = kwargs.get("index")
        if not index:
            raise Exception("ElasticsearchRepository error: Index must be set")
        try:
            response = await self.elastic_client.search(**kwargs)

            docs = response.get("hits", {}).get("hits", [])
            docs_dicts = [doc["_source"] for doc in docs]
            return docs_dicts

        except NotFoundError as e:
            logger.debug(
                f"No documents found in index={index} with params={kwargs}. Exception: {e}"
            )
            return []
        except BadRequestError as e:
            logger.error(
                f"BadRequestError while fetching documents from index={index} with params={kwargs}: {e}"
            )
            raise
