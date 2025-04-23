import pytest
from testdata.samples.users import user_sample, user_history_sample
from auth.src.models.entity import User, LoginHistory
from typing import Any
from http import HTTPStatus


@pytest.mark.asyncio
async def test_profile(pg_write_data: Any, make_get_request: Any) -> None:
    pg_write_data(User, user_sample)
    uuid = user_sample[0]["uuid"]

    response = await make_get_request(f"profile/{uuid}")
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 1
    assert response.body["uuid"] == uuid

    response = await make_get_request(f"profile/f8557b55-c2c6-4613-8a6d-e459f3456005")
    assert response.status == HTTPStatus.NOT_FOUND
    assert len(response.body) == 0


@pytest.mark.asyncio
async def test_history(pg_write_data: Any, make_get_request: Any) -> None:
    pg_write_data(User, user_sample)
    uuid = user_sample[0]["uuid"]

    pg_write_data(LoginHistory, user_history_sample)
    event_uuid = user_history_sample[0]["uuid"]

    response = await make_get_request(f"profile/{uuid}/history")
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 5
    assert response.body["uuid"] == event_uuid


@pytest.mark.asyncio
async def test_reset_password(pg_write_data: Any, make_post_request: Any) -> None:
    pg_write_data(User, user_sample)
    uuid = user_sample[0]["uuid"]

    response = await make_post_request(f"profile/{uuid}/reset/password")
    assert response.status == HTTPStatus.OK


@pytest.mark.asyncio
async def test_reset_login(pg_write_data: Any, make_post_request: Any) -> None:
    pg_write_data(User, user_sample)
    uuid = user_sample[0]["uuid"]

    response = await make_post_request(f"profile/{uuid}/reset/login")
    assert response.status == HTTPStatus.OK
