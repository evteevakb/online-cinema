"""
Test suite for the 'persons' API endpoints.
"""

import uuid
from http import HTTPStatus

import pytest

from testdata.samples.persons import person_sample, film_sample, person_sample_search, film_sample_search


@pytest.mark.asyncio(loop_scope="session")
class TestPersonDetails:
    """Tests for the `/persons/{uuid}` endpoint"""

    async def test_nonexistent_person(
        self,
        make_get_request,
    ) -> None:
        random_uuid = str(uuid.uuid4())
        response = await make_get_request(f"persons/{random_uuid}")
        assert response.status == HTTPStatus.NOT_FOUND

    async def test_existing_person(
        self,
        make_get_request,
        es_write_data,
    ) -> None:
        await es_write_data(index="persons", es_data=person_sample)
        await es_write_data(index="movies", es_data=film_sample)

        for idx, person in enumerate(person_sample):
            uuid = person["id"]
            response = await make_get_request(f"persons/{uuid}")
            assert response.status == HTTPStatus.OK
            assert response.body["uuid"] == uuid
            assert response.body["full_name"] == person["full_name"]
            assert response.body["films"][idx]["uuid"] == film_sample[idx]["id"]
            assert "roles" in response.body["films"][idx]
            assert "actor" in response.body["films"][idx]["roles"]

    async def test_cache(
            self,
            make_get_request,
            es_write_data,
            redis_client,
    ) -> None:
        await es_write_data(index="persons", es_data=person_sample)
        await es_write_data(index="movies", es_data=film_sample)

        uuid = person_sample[0]["id"]
        redis_key = f"person:{uuid}"

        await redis_client.delete(redis_key)
        cached_before = await redis_client.get(redis_key)
        response = await make_get_request(f"persons/{uuid}")
        cached_after = await redis_client.get(redis_key)

        assert cached_before is None
        assert response.status == HTTPStatus.OK
        assert cached_after is not None


@pytest.mark.asyncio(loop_scope="session")
class TestPersonFilms:
    """Tests for the `/persons/{uuid}/film` endpoint"""
    async def test_person_films(
        self,
        make_get_request,
        es_write_data,
    ) -> None:
        await es_write_data(index="persons", es_data=person_sample)
        await es_write_data(index="movies", es_data=film_sample)

        for idx, person in enumerate(person_sample):
            uuid = person["id"]
            expected_films = [
                film for film in film_sample if any(actor["id"] == uuid for actor in film["actors"])
            ]

            response = await make_get_request(f"persons/{uuid}/film")

            films = response.body

            assert response.status == HTTPStatus.OK
            assert isinstance(films, list)
            assert len(films) == len(expected_films)

            for film_resp in films:
                assert any(film_resp["uuid"] == film["id"] for film in expected_films)

    async def test_cache(
            self,
            make_get_request,
            es_write_data,
            redis_client,
    ) -> None:
        await es_write_data(index="persons", es_data=person_sample)
        await es_write_data(index="movies", es_data=film_sample)

        uuid = person_sample[0]["id"]
        redis_key = f"person_films:{uuid}"

        await redis_client.delete(redis_key)
        cached_before = await redis_client.get(redis_key)
        response = await make_get_request(f"persons/{uuid}/film")
        cached_after = await redis_client.get(redis_key)

        assert cached_before is None
        assert response.status == HTTPStatus.OK
        assert cached_after is not None


@pytest.mark.asyncio(loop_scope="session")
class TestPersonSearch:
    """Tests for the `/persons/search` endpoint"""

    async def test_persons_search_no_results(
            self,
            make_get_request,
            es_write_data
    ) -> None:
        await es_write_data(index="persons", es_data=person_sample_search)

        query = "someRandomQueryThatMatchesNoOne123"
        page_number = 1
        page_size = 20
        sort = "full_name"

        response = await make_get_request(
            f"persons/search?query={query}&page_number={page_number}&page_size={page_size}&sort={sort}"
        )

        assert response.status == HTTPStatus.OK
        assert response.body == [] or len(response.body) == 0

    async def test_persons_search_query_sort(
        self,
        make_get_request,
        es_write_data,
    ) -> None:
        await es_write_data(index="persons", es_data=person_sample_search)
        await es_write_data(index="movies", es_data=film_sample_search)

        query = "arnold"
        page_number = 1
        page_size = 20
        sort = "full_name"

        response = await make_get_request(
            f"persons/search?query={query}&page_number={page_number}&page_size={page_size}&sort={sort}"
        )

        persons = response.body
        names = [p["full_name"] for p in persons]
        goal_len = len([p for p in person_sample_search if query.lower() in p["full_name"].lower()])

        assert response.status == HTTPStatus.OK
        assert isinstance(persons, list)

        for person in persons:
            assert query.lower() in person["full_name"].lower()

        assert goal_len == len(persons)
        assert names == sorted(names)

    async def test_persons_search_cache(
            self,
            make_get_request,
            es_write_data,
            redis_client,
    ) -> None:
        await es_write_data(index="persons", es_data=person_sample_search)
        await es_write_data(index="movies", es_data=film_sample_search)

        query = "arnold"
        page_number = 1
        page_size = 20
        sort = "full_name"
        redis_key = f"persons:{query}:{sort}:{page_number}:{page_size}"

        await redis_client.delete(redis_key)
        cached_before = await redis_client.get(redis_key)
        response = await make_get_request(
            f"persons/search?query={query}&page_number={page_number}&page_size={page_size}&sort={sort}"
        )
        cached_after = await redis_client.get(redis_key)

        assert cached_before is None
        assert response.status == HTTPStatus.OK
        assert cached_after is not None
