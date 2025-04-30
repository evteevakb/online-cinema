from functools import lru_cache
from typing import List, Type

from elasticsearch import AsyncElasticsearch
from fastapi import Depends, Query, HTTPException
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.cache import BaseCache, RedisCache
from services.queries.film_query import FilmElasticQueryBuilder
from services.storage import BaseRepository, ElasticsearchRepository
from starlette import status
from utils.auth import Roles
from schemas.auth import AuthorizationResponse

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
ALLOWED_ROLES_PAID_FILMS = [Roles.ADMIN, Roles.SUPERUSER, Roles.PAID_USER]

class FilmService:
    def __init__(
        self, cache: BaseCache, repository: BaseRepository, query_builder: Type
    ) -> None:
        self.cache = cache
        self.repository = repository
        self.query_builder = query_builder

    async def get_by_uuid(
        self,
        film_uuid: str,
        user_with_roles: AuthorizationResponse
    ) -> Film | None:
        cache_key = f"film:{film_uuid}"
        film = await self.cache.get(key=cache_key)
        if film:
            return Film.model_validate_json(film)
        film = await self._get_film_from_repository(film_uuid)
        film_is_paid = film.paid_only
        if film_is_paid and not any(role in user_with_roles.roles for role in ALLOWED_ROLES_PAID_FILMS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This operation is forbidden for you",
            )
        if film:
            await self.cache.set(
                key=cache_key,
                value=film.model_dump_json(),
                expire=FILM_CACHE_EXPIRE_IN_SECONDS,
            )
        return film

    async def get_all(
        self,
        page_size: int,
        page_number: int,
        query: str | None = None,
        sort: str | None = None,
        genre: str | None = None,
    ) -> List[Film]:
        cache_key = f"films:{query}:{sort}:{page_number}:{page_size}:{genre}"
        cached_films = await self.cache.get(cache_key)
        if cached_films:
            return [Film.model_validate_json(film) for film in cached_films]

        films = await self._get_films_from_repository(
            page_size=page_size,
            page_number=page_number,
            query=query,
            sort=sort,
            genre=genre,
        )
        if films:
            await self.cache.set(
                key=cache_key,
                value=[film.model_dump_json() for film in films],
                expire=FILM_CACHE_EXPIRE_IN_SECONDS,
            )
        return films

    async def _get_film_from_repository(
        self,
        film_uuid: str,
    ) -> Film | None:
        film = await self.repository.get_by_id(id=film_uuid, index="movies")
        if film is not None:
            return Film(**film)

    async def _get_films_from_repository(
        self,
        page_size: int,
        page_number: int,
        query: str | None = None,
        sort: str | None = None,
        genre: str | None = None,
    ) -> List[Film]:
        query = await self.query_builder.get_film_search_query(
            page_size=page_size,
            page_number=page_number,
            query=query,
            sort=sort,
            genre=genre,
        )

        films_raw = await self.repository.get_list(index="movies", body=query)

        return [Film(**doc) for doc in films_raw]


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(
        cache=RedisCache(redis_client=redis),
        repository=ElasticsearchRepository(elastic_client=elastic),
        query_builder=FilmElasticQueryBuilder(),
    )


def film_filters(
    sort: str | None = Query(None, regex="^-?imdb_rating$"),
    genre: str | None = None,
    page_size: int = Query(10, ge=1),
    page_number: int = Query(1, ge=1),
) -> dict:
    return {
        "sort": sort,
        "genre": genre,
        "page_size": page_size,
        "page_number": page_number,
    }
