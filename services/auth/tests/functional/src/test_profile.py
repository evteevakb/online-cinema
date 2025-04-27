import pytest
from testdata.samples.users import user, user_history
from models.entity import User, LoginHistory
from typing import Any, AsyncGenerator
from http import HTTPStatus
from sqlalchemy.future import select


@pytest.mark.asyncio
async def test_profile(pg_write_data: Any, make_get_request: Any, db_session: Any, refresh_db, clean_tables) -> None:
    user_sample = user()
    await pg_write_data(User, user_sample)

    async with db_session as session:
        result = await session.execute(
            select(User.uuid).where(User.email == user_sample[0]["email"])
        )
        user_uuid = result.scalar_one()
        count = await session.execute(select(User))
        len_users = len(count.scalars().all())
        assert len_users == len(user_sample)
        result = await session.execute(select(User).where(User.uuid == user_uuid))
        result = result.scalar_one_or_none()
        assert result is not None

    response = await make_get_request(f"profile/{user_uuid}")
    assert response.status == HTTPStatus.OK
    assert response.body["uuid"] == str(user_uuid)

    response = await make_get_request(f"profile/f8557b55-c2c6-4613-8a6d-e459f3456005")
    assert response.status == 404


@pytest.mark.asyncio
async def test_history(pg_write_data: Any, make_get_request: Any, db_session: Any, clean_tables: Any) -> None:
    user_sample = user()
    await pg_write_data(User, user_sample)

    async with db_session as session:
        result = await session.execute(
            select(User.uuid).where(User.email == user_sample[0]["email"])
        )
        user_uuid = result.scalar_one()
        second_result = await session.execute(
            select(User))
        users = second_result.scalars().all()
        user_history_sample = user_history(users)
        await pg_write_data(LoginHistory, user_history_sample)
        event_uuid = await session.execute(
            select(LoginHistory.uuid).where(LoginHistory.user_uuid == user_uuid)
        )
        event_uuid = str(event_uuid.scalars().all()[0])

    response = await make_get_request(f"profile/{user_uuid}/history")

    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    assert response.body[0]["uuid"] == event_uuid
    assert any(item["uuid"] == event_uuid for item in response.body)


@pytest.mark.asyncio
async def test_reset_password(pg_write_data: Any, make_post_request: Any, db_session: Any, clean_tables: Any) -> None:
    user_sample = user()
    new_pass = {"password": "new_pass"}
    await pg_write_data(User, user_sample)
    async with db_session as session:
        result = await session.execute(
            select(User.uuid).where(User.email == user_sample[0]["email"])
        )
        user_uuid = result.scalar_one()

    response = await make_post_request(f"profile/{user_uuid}/reset/password", new_pass)
    assert response.status == HTTPStatus.OK


@pytest.mark.asyncio
async def test_reset_login(pg_write_data: Any, make_post_request: Any, db_session: Any, clean_tables: Any) -> None:
    user_sample = user()
    new_login = {"login": "new_email@gmail.com"}
    await pg_write_data(User, user_sample)
    async with db_session as session:
        result = await session.execute(
            select(User.uuid).where(User.email == user_sample[0]["email"])
        )
        user_uuid = result.scalar_one()

    response = await make_post_request(f"profile/{user_uuid}/reset/login", new_login)
    assert response.status == HTTPStatus.OK
