from functools import lru_cache
import logging
from typing import List, Type

from elasticsearch import AsyncElasticsearch
from fastapi import Depends, Query
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import FilmBase
from models.person import FilmPerson, Person, PersonRole
from services.cache import BaseCache, RedisCache
from services.storage import BaseRepository, ElasticsearchRepository

from services.queries.person_query import PersonElasticQueryBuilder

logger = logging.getLogger(__name__)

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    def __init__(
        self, cache: BaseCache, repository: BaseRepository, query_builder: Type
    ) -> None:
        self.cache = cache
        self.repository = repository
        self.query_builder = query_builder

    async def get_person(
        self,
        person_uuid: str,
    ) -> Person | None:
        cache_key = f"person:{person_uuid}"
        person = await self.cache.get(cache_key)
        if person:
            return Person.model_validate_json(person)
        person = await self._get_person_from_repository(person_uuid)
        if person:
            await self.cache.set(
                key=cache_key,
                value=person.model_dump_json(),
                expire=PERSON_CACHE_EXPIRE_IN_SECONDS,
            )
        return person

    async def get_films_by_person(
        self,
        person_uuid: str,
    ) -> List[FilmBase]:
        """Получение фильмов по ID персоны с кэшированием."""
        cache_key = f"person_films:{person_uuid}"
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return [FilmBase.model_validate_json(film) for film in cached_data]

        films = await self._get_films_by_person_from_repository(person_uuid)
        if films:
            await self.cache.set(
                key=cache_key,
                value=[film.model_dump_json() for film in films],
                expire=PERSON_CACHE_EXPIRE_IN_SECONDS,
            )
        return films

    async def search_persons(
        self,
        query: str,
        page_number: int,
        page_size: int,
        sort: str | None = None,
    ) -> list[Person]:
        cache_key = f"persons:{query}:{sort}:{page_number}:{page_size}"
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return [Person.model_validate_json(film) for film in cached_data]

        es_query = await self.query_builder.get_person_search_query(
            query=query, page_number=page_number, page_size=page_size, sort=sort
        )

        persons_raw = await self.repository.get_list(index="persons", body=es_query)

        persons = []

        for person in persons_raw:
            person_uuid = person.get("id")
            full_name = person.get("full_name", "")

            films = await self._get_person_films(person_uuid)
            persons.append(Person(id=person_uuid, name=full_name, films=films))
        if persons:
            await self.cache.set(
                key=cache_key,
                value=[person.model_dump_json() for person in persons],
                expire=PERSON_CACHE_EXPIRE_IN_SECONDS,
            )
        return persons

    async def _get_films_by_person_from_repository(
        self,
        person_uuid: str,
    ) -> list[FilmBase]:

        query = await self.query_builder.get_films_by_person_uuid_query(
            person_uuid=person_uuid
        )

        movies = await self.repository.get_list(index="movies", body=query)

        films = []
        for film in movies:
            films.append(
                FilmBase(
                    id=film.get("id"),
                    title=film.get("title"),
                    imdb_rating=film.get("imdb_rating"),
                )
            )

        return films

    async def _get_person_films(
        self,
        person_uuid: str,
    ) -> list[FilmPerson] | None:

        query = await self.query_builder.get_films_by_person_uuid_query(
            person_uuid=person_uuid
        )

        movies = await self.repository.get_list(index="movies", body=query)

        films = []

        for film in movies:
            roles = []

            if any(actor["id"] == person_uuid for actor in film.get("actors", [])):
                roles.append(PersonRole.ACTOR)
            if any(
                director["id"] == person_uuid for director in film.get("directors", [])
            ):
                roles.append(PersonRole.DIRECTOR)
            if any(writer["id"] == person_uuid for writer in film.get("writers", [])):
                roles.append(PersonRole.WRITER)

            if roles:
                films.append(FilmPerson(id=film.get("id"), roles=roles))

        return films

    async def _get_person_from_repository(
        self,
        person_uuid: str,
    ) -> Person | None:
        person = await self.repository.get_by_id(id=person_uuid, index="persons")
        if person is not None:
            films = await self._get_person_films(person_uuid)
            return Person(
                id=person.get("id"), name=person.get("full_name"), films=films
            )


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(
        cache=RedisCache(redis_client=redis),
        repository=ElasticsearchRepository(elastic_client=elastic),
        query_builder=PersonElasticQueryBuilder(),
    )


def person_filters(
    page_number: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    sort: str | None = Query(None, regex="^-?full_name$"),
) -> dict:
    return {
        "sort": sort,
        "page_size": page_size,
        "page_number": page_number,
    }
