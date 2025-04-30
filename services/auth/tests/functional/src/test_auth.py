from http import HTTPStatus, HTTPMethod

import pytest


@pytest.mark.asyncio
async def test_register(make_request):
    payload = {
        "email": "user1@example.com",
        "password": "StrongPass123!"
    }

    response = await make_request(HTTPMethod.POST, "auth/registration", payload)

    assert response.status == HTTPStatus.OK

    response_json = response.body
    assert "access_token" in response_json
    assert "refresh_token" in response_json


@pytest.mark.asyncio
async def test_login(make_request):
    login_payload = {
        "email": "user3@example.com",
        "password": "P@ssw0rd1"
    }

    register_response = await make_request(HTTPMethod.POST, "auth/registration", login_payload)
    assert register_response.status == HTTPStatus.OK
    login_response = await make_request(HTTPMethod.POST, "auth/login", login_payload)
    assert login_response.status == HTTPStatus.OK
    response_json = login_response.body
    assert "access_token" in response_json
    assert "refresh_token" in response_json


@pytest.mark.asyncio
async def test_logout(make_request):
    login_payload = {
        "email": "user4@example.com",
        "password": "P@ssw0rd"
    }


    register_response = await make_request(HTTPMethod.POST, "auth/registration", login_payload)
    assert register_response.status == HTTPStatus.OK
    login_response = await make_request(HTTPMethod.POST, "auth/login", login_payload)
    assert login_response.status == HTTPStatus.OK
    response_json = login_response.body
    logout_payload = {
        "access_token": response_json.get('access_token'),
        "refresh_token": response_json.get('refresh_token')
    }

    logout_response = await make_request(HTTPMethod.POST, "auth/logout", logout_payload)
    assert logout_response.status == HTTPStatus.OK


@pytest.mark.asyncio
async def test_refresh(make_request):
    login_payload = {
        "email": "user4@example.com",
        "password": "P@ssw0rd"
    }


    register_response = await make_request(HTTPMethod.POST, "auth/registration", login_payload)
    assert register_response.status == HTTPStatus.OK
    login_response = await make_request(HTTPMethod.POST, "auth/login", login_payload)
    assert login_response.status == HTTPStatus.OK
    logout_payload = {
        "refresh_token": login_response.body.get('refresh_token')
    }

    refresh_response = await make_request(HTTPMethod.POST, "auth/refresh", logout_payload)
    assert refresh_response.status == HTTPStatus.OK