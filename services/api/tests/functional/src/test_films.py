"""
Test suite for the 'films' API endpoints.
"""

from http import HTTPStatus
import uuid

import pytest

from testdata.samples.films import films_sample


@pytest.mark.asyncio(loop_scope="session")
class TestFilms:
    """Tests for /films endpoint"""

    async def test_empty_response(
        self,
        refresh,
        make_get_request,
    ) -> None:
        """Ensures that an empty list is returned when the index is empty"""
        await refresh("movies")
        response = await make_get_request("films")

        assert response.status == HTTPStatus.OK
        assert len(response.body) == 0

    @pytest.mark.parametrize(
        "params",
        [
            {
                "page_size": 5,
                "page_number": 1,
            },
            None,
        ],
    )
    async def test_nonempty_response(
        self,
        params,
        make_get_request,
        es_write_data,
    ) -> None:
        """Ensures that a non-empty list of films is returned after inserting data.
        Supports optional pagination parameters."""
        await es_write_data(index="movies", es_data=films_sample)
        response = await make_get_request("films", params=params)

        assert response.status == HTTPStatus.OK
        assert len(response.body) == len(films_sample)

    async def test_empty_pagination(
        self,
        make_get_request,
        es_write_data,
    ) -> None:
        """Ensures that requesting a non-existent page returns an empty result"""
        await es_write_data(index="movies", es_data=films_sample)
        response = await make_get_request(
            "films", params={"page_size": len(films_sample), "page_number": 2}
        )

        assert response.status == HTTPStatus.OK
        assert len(response.body) == 0

    @pytest.mark.parametrize(
        "params",
        [
            {
                "page_size": 0,
                "page_number": 1,
            },
            {
                "page_size": -1,
                "page_number": 1,
            },
            {
                "page_size": 5,
                "page_number": 0,
            },
            {
                "page_size": 5,
                "page_number": -1,
            },
        ],
    )
    async def test_invalid_pagination(
        self,
        make_get_request,
        params,
    ) -> None:
        """Ensures that invalid pagination parameters are handled correctly"""
        response = await make_get_request("films", params=params)

        assert response.status == HTTPStatus.UNPROCESSABLE_CONTENT

    async def test_cache(
        self,
        refresh,
        make_get_request,
        es_write_data,
        redis_client,
    ) -> None:
        """Ensure that film list responses are cached"""
        await refresh("movies")
        key = f"films:None:None:1:{len(films_sample)}:None"

        cache_before = await redis_client.get(key)
        assert cache_before is None

        await es_write_data(index="movies", es_data=films_sample)
        await make_get_request("films", params={"page_size": len(films_sample), "page_number": 1})
        cache = await redis_client.get(key)

        assert cache is not None

    async def test_genre_param(
        self,
        make_get_request,
    ):
        """Ensure that genre param works correctly"""
        genre_id = films_sample[2]["genres"][1]["id"]
        response = await make_get_request("films", params={"genre": genre_id})
        goal_len = len([
            film for film in films_sample
            if genre_id in [g["id"] for g in film["genres"]]
        ])

        assert len(response.body) == goal_len


@pytest.mark.asyncio(loop_scope="session")
class TestFilmDetails:
    """Tests for the `/films/{uuid}` endpoint"""

    async def test_nonexistent_uuid(
        self,
        make_get_request,
    ) -> None:
        """Ensures that a 404 is returned when a nonexistent UUID is requested"""
        random_uuid = str(uuid.uuid4())
        response = await make_get_request(f"films/{random_uuid}")

        assert response.status == HTTPStatus.NOT_FOUND

    async def test_correct_uuid(
        self,
        make_get_request,
        es_write_data,
    ) -> None:
        """Ensures that the correct film is returned when a valid UUID is requested"""
        await es_write_data(index="movies", es_data=films_sample)
        film = films_sample[0]
        uuid = film["id"]

        response = await make_get_request(f"films/{uuid}")
        body = response.body

        assert response.status == HTTPStatus.OK
        assert body["uuid"] == uuid
        assert body["title"] == film["title"]
        assert body["description"] == film["description"]
        assert body["imdb_rating"] == film["imdb_rating"]
        assert len(body["genres"]) == len(film["genres"])
        assert len(body["directors"]) == len(film["directors_names"])
        assert len(body["actors"]) == len(film["actors_names"])
        assert len(body["writers"]) == len(film["writers_names"])

    async def test_cache(
        self,
        refresh,
        make_get_request,
        es_write_data,
        redis_client,
    ) -> None:
        """Ensures that film detail responses are cached"""
        await refresh("movies")
        film = films_sample[0]
        uuid = film["id"]
        key = f"film:{uuid}"

        cache_before = await redis_client.get(key)
        assert cache_before is None

        await es_write_data(index="movies", es_data=films_sample)
        await make_get_request(f"films/{uuid}")
        cache = await redis_client.get(key)

        assert cache is not None


@pytest.mark.asyncio(loop_scope="session")
class TestSearchFilms:
    """Tests for /search of films endpoint"""

    async def test_films_search_empty_results(
            self,
            refresh,
            make_get_request,
            es_write_data
    ) -> None:
        await refresh("movies")
        await es_write_data(index="movies", es_data=films_sample)

        query = "non-existentQuery123"
        page_number = 1
        page_size = 20
        sort = "-imdb_rating"

        response = await make_get_request(
            "films/search",
            params={"query": query,
                    "page_number": page_number,
                    "page_size": page_size,
                    "sort": sort}
        )

        assert response.status == HTTPStatus.OK
        assert len(response.body) == 0

    async def test_films_search_query_sort(
        self,
        make_get_request,
        es_write_data,
    ) -> None:

        await es_write_data(index="movies", es_data=films_sample)

        query = "wars"
        page_number = 1
        page_size = 20
        sort = "-imdb_rating"

        response = await make_get_request(
            "films/search",
            params={"query": query,
                    "page_number": page_number,
                    "page_size": page_size,
                    "sort": sort}
        )

        assert response.status == HTTPStatus.OK
        films = response.body
        assert isinstance(films, list)

        for film in films:
            assert query.lower() in film["title"].lower()

        goal_len = len([film for film in films_sample if query.lower() in film["title"].lower()])
        assert goal_len == len(films)

        ratings = [f["imdb_rating"] for f in films]
        assert ratings == sorted(ratings, reverse=True)

    async def test_films_search_cache(
            self,
            refresh,
            make_get_request,
            es_write_data,
            redis_client,
    ) -> None:

        await refresh("movies")
        await es_write_data(index="movies", es_data=films_sample)

        query = "wars"
        page_number = 1
        page_size = 20
        sort = "imdb_rating"

        key = f"films:{query}:{sort}:{page_number}:{page_size}:None"

        cached_before = await redis_client.get(key)
        assert cached_before is None

        response = await make_get_request(
            "films/search",
            params={"query": query,
                    "page_number": page_number,
                    "page_size": page_size,
                    "sort": sort}
        )

        assert response.status == HTTPStatus.OK

        cached_after = await redis_client.get(key)
        assert cached_after is not None