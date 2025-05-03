from http import HTTPMethod, HTTPStatus
from typing import Any

import pytest
from sqlalchemy.future import select
from sqlalchemy import func


from models.entity import LoginHistory, User
from testdata.samples.roles import all_role_names, Roles
from testdata.samples.users import user, user_history
from utils.auth import create_access_token


@pytest.mark.asyncio
async def test_profile(
    pg_write_data: Any,
    make_request: Any,
    db_session: Any,
) -> None:
    user_sample = user()
    await pg_write_data(User, user_sample)

    async with db_session as session:
        result = await session.execute(
            select(User.uuid).where(User.email == user_sample[0]["email"])
        )
        user_uuid = result.scalar_one()
        user_email = user_sample[0]["email"]
        count = await session.execute(select(User))
        len_users = len(count.scalars().all())
        assert len_users == len(user_sample)
        result = await session.execute(select(User).where(User.uuid == user_uuid))
        result = result.scalar_one_or_none()
        assert result is not None

    response = await make_request(HTTPMethod.GET, f"profile/{user_email}")
    assert response.status == HTTPStatus.OK
    assert response.body["uuid"] == str(user_uuid)

    response = await make_request(
        HTTPMethod.GET, "profile/f8557b55-c2c6-4613-8a6d-e459f3456005"
    )
    assert response.status == 404


@pytest.mark.asyncio
async def test_history(
    pg_write_data: Any,
    make_request: Any,
    db_session: Any,
    create_roles: Any,
    create_user: Any,
) -> None:
    user_sample = user()
    user_role = Roles.USER.value
    await create_roles(all_role_names)
    user_created = await create_user(**user_sample[0], role_names=[user_role])
    user_token = create_access_token(user_created)
    await pg_write_data(User, user_sample[1:])

    async with db_session as session:
        result = await session.execute(
            select(User.uuid).where(User.email == user_sample[0]["email"])
        )
        user_uuid = result.scalar_one()
        second_result = await session.execute(select(User))
        users = second_result.scalars().all()
        user_history_sample = user_history(users)
        await pg_write_data(LoginHistory, user_history_sample)
        event_uuid = await session.execute(
            select(LoginHistory.uuid).where(LoginHistory.user_uuid == user_uuid)
        )
        event_uuid = str(event_uuid.scalars().all()[0])


    async with db_session as session:
        count = await session.scalar(
            select(func.count()).where(LoginHistory.user_uuid == user_uuid)
        )
        assert count == 15

    response = await make_request(
        method=HTTPMethod.GET,
        endpoint=f"profile/{user_uuid}/history?page=2&size=10",
        token=user_token,
    )

    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, dict)
    assert len(response.body["data"]) == 5
    assert response.body["total"] == 15
    assert response.body["page"] == 2
    assert response.body["size"] == 10

    assert any(item["uuid"] == event_uuid for item in response.body["data"]), f"Expected one of ids of event equal {event_uuid}, but get instead {response.body['data']}"


@pytest.mark.asyncio
async def test_reset_password(
    pg_write_data: Any,
    make_request: Any,
) -> None:
    user_sample = user()
    email = user_sample[0]["email"]
    body = {
        "login": user_sample[0]["email"],
        "password": user_sample[0]["password"],
        "new_password": "new_pass",
    }
    await pg_write_data(User, user_sample)

    response = await make_request(
        HTTPMethod.POST, f"profile/{email}/reset/password", body
    )
    assert response.status == HTTPStatus.OK


@pytest.mark.asyncio
async def test_reset_login(
    pg_write_data: Any,
    make_request: Any,
) -> None:
    user_sample = user()
    email = user_sample[0]["email"]
    body = {
        "login": email,
        "new_login": "new_email@gmail.com",
        "password": user_sample[0]["password"],
    }
    await pg_write_data(User, user_sample)

    response = await make_request(HTTPMethod.POST, f"profile/{email}/reset/login", body)
    assert response.status == HTTPStatus.OK
