"""
Manages genres using Redis as a cache and Elasticsearch as the primary data source.
"""

from typing import Type

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.cache import BaseCache, RedisCache
from services.queries.genre_query import GenreElasticQueryBuilder
from services.storage import BaseRepository, ElasticsearchRepository

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService:
    """Service for managing genres."""

    def __init__(
        self, cache: BaseCache, repository: BaseRepository, query_builder: Type
    ) -> None:
        """Initialize the GenreService.

        Args:
            cache (BaseCache): an instance for caching.
            repository (BaseRepository): an instance for retrieving data.
        """
        self.cache = cache
        self.repository = repository
        self.query_builder = query_builder

    async def get_genre_by_uuid(
        self,
        genre_uuid: str,
    ) -> Genre | None:
        """Retrieve a single genre by its UUID.

        Args:
            genre_uuid (str): the UUID of the genre.

        Returns:
            Genre | None: a Genre object if found, otherwise None.
        """
        cache_key = f"genre:{genre_uuid}"
        genre = await self.cache.get(cache_key)
        if genre:
            return Genre.model_validate_json(genre)
        genre = await self._get_genre_from_repository(genre_uuid)
        if genre:
            await self.cache.set(
                key=cache_key,
                value=genre.model_dump_json(),
                expire=GENRE_CACHE_EXPIRE_IN_SECONDS,
            )
        return genre

    async def get_all(
        self,
        page_size: int,
        page_number: int,
    ) -> list[Genre] | None:
        """Retrieve a paginated list of genres.

        Args:
            page_size (int): number of items per page.
            page_number (int): the page number to retrieve.

        Returns:
            list[Genre] | None: a list of Genre objects or None if no genres are found.
        """
        cache_key = f"genres:{page_size}:{page_number}"
        cached_genres = await self.cache.get(cache_key)
        if cached_genres:
            return [Genre.model_validate_json(genre) for genre in cached_genres]
        genres = await self._get_genres_from_repository(page_size, page_number)
        if genres:
            await self.cache.set(
                key=cache_key,
                value=[genre.model_dump_json() for genre in genres],
                expire=GENRE_CACHE_EXPIRE_IN_SECONDS,
            )
        return genres

    async def _get_genre_from_repository(
        self,
        genre_uuid: str,
    ) -> Genre | None:
        """Fetch a single genre from ElasticsearchRepository by its UUID.

        Args:
            genre_uuid (str): the UUID of the genre.

        Returns:
            Genre | None: a Genre object if found, otherwise None.
        """
        genre = await self.repository.get_by_id(id=genre_uuid, index="genres")
        if genre is not None:
            return Genre(**genre)

    async def _get_genres_from_repository(
        self,
        page_size: int,
        page_number: int,
    ) -> list[Genre]:
        """Fetch genres from Elasticsearch with pagination.

        Args:
            page_size (int): number of items per page.
            page_number (int): the page number to retrieve.

        Returns:
            list[Genre]: a list of Genre objects.
        """

        query = await self.query_builder.get_genre_search_query(
            page_number=page_number, page_size=page_size
        )

        docs = await self.repository.get_list(
            index="genres",
            body=query,
        )
        return [Genre(**doc) for doc in docs]


def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    """Dependency injection function to provide an instance of GenreService.

    Args:
        redis (Redis): Redis instance.
        elastic (AsyncElasticsearch): Elasticsearch instance.

    Returns:
        GenreService: an instance of GenreService.
    """
    return GenreService(
        cache=RedisCache(redis_client=redis),
        repository=ElasticsearchRepository(elastic_client=elastic),
        query_builder=GenreElasticQueryBuilder(),
    )
