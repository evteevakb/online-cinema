"""
Test suite for the 'genres' API endpoints.
"""

from http import HTTPStatus
import uuid

import pytest

from testdata.samples.genres import genre_sample


@pytest.mark.asyncio(loop_scope="session")
class TestGenres:
    """Tests for /genres endpoint"""

    async def test_empty_response(
        self,
        refresh,
        make_get_request,
    ) -> None:
        """Ensures that an empty list is returned when the index is empty"""
        await refresh("genres")
        response = await make_get_request("genres")

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
        """Ensures that a non-empty list of genres is returned after inserting data.
        Supports optional pagination parameters."""
        await es_write_data(index="genres", es_data=genre_sample)
        response = await make_get_request("genres", params=params)

        assert response.status == HTTPStatus.OK
        assert len(response.body) == len(genre_sample)

    async def test_empty_pagination(
        self,
        make_get_request,
        es_write_data,
    ) -> None:
        """Ensures that requesting a non-existent page returns an empty result"""
        await es_write_data(index="genres", es_data=genre_sample)
        response = await make_get_request(
            "genres", params={"page_size": len(genre_sample), "page_number": 2}
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
        response = await make_get_request("genres", params=params)

        assert response.status == HTTPStatus.UNPROCESSABLE_CONTENT

    async def test_cache(
        self,
        make_get_request,
        es_write_data,
        redis_client,
    ) -> None:
        """Ensure that genre list responses are cached"""
        await es_write_data(index="genres", es_data=genre_sample)

        await make_get_request(
            "genres", params={"page_size": len(genre_sample), "page_number": 1}
        )
        response = await redis_client.get(f"genres:{len(genre_sample)}:1")

        assert response is not None


@pytest.mark.asyncio(loop_scope="session")
class TestGenreDetails:
    """Tests for the `/genres/{uuid}` endpoint"""

    async def test_nonexistent_uuid(
        self,
        make_get_request,
    ) -> None:
        """Ensures that a 404 is returned when a nonexistent UUID is requested"""
        random_uuid = str(uuid.uuid4())
        response = await make_get_request(f"genres/{random_uuid}")

        assert response.status == HTTPStatus.NOT_FOUND

    async def test_correct_uuid(
        self,
        make_get_request,
        es_write_data,
    ) -> None:
        """Ensures that the correct genre is returned when a valid UUID is requested"""
        await es_write_data(index="genres", es_data=genre_sample)
        uuid = genre_sample[0]["id"]
        response = await make_get_request(f"genres/{uuid}")

        assert response.status == HTTPStatus.OK
        assert response.body["uuid"] == uuid
        assert response.body["name"] == genre_sample[0]["name"]

    async def test_cache(
        self,
        make_get_request,
        es_write_data,
        redis_client,
    ) -> None:
        """Ensures that genre detail responses are cached"""
        await es_write_data(index="genres", es_data=genre_sample)
        uuid = genre_sample[0]["id"]

        await make_get_request(f"genres/{uuid}")
        response = await redis_client.get(f"genre:{uuid}")

        assert response is not None
