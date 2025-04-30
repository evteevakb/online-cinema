"""
API fixtures for functional tests.
"""

from typing import Any, AsyncGenerator, Awaitable, Callable

from http import HTTPMethod
import aiohttp
import pytest_asyncio
from pydantic import BaseModel
from settings import APISettings

api_settings = APISettings()


class Response(BaseModel):
    """Represents a HTTP response object."""

    body: Any
    status: int


@pytest_asyncio.fixture(name="session")
async def session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    """Provides a shared aiohttp client session for all tests in the session.

    Yields:
        aiohttp.ClientSession: an asynchronous HTTP client session.
    """
    async with aiohttp.ClientSession() as session:
        yield session


@pytest_asyncio.fixture(name="make_request")
def make_request(session) -> Callable[[HTTPMethod, str, dict[str, Any] | None], Awaitable[Response]]:
    """Fixture for making HTTP requests to the API.

    Args:
        session (aiohttp.ClientSession): the shared client session.

    Returns:
        Callable: an async function to perform requests.
    """
    async def inner(
        method: HTTPMethod,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        token: str | None = None,
    ) -> Response:
        params = params or {}
        url = api_settings.base_url + endpoint

        request_func = {
            "GET": session.get,
            "POST": session.post,
            "PATCH": session.patch,
            "PUT": session.put,
            "DELETE": session.delete,
        }.get(method)

        if request_func is None:
            raise ValueError(f"Unsupported HTTP method: {method}")

        headers = {}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        request_kwargs = {"headers": headers} if headers else {}

        async with request_func(url, params=params, json=json, **request_kwargs) as response:

            try:
                body = await response.json()
            except aiohttp.ContentTypeError:
                body = await response.text()

            status = response.status
            if 500 <= status < 600:
                raise RuntimeError(f"{status}: {body}")

            return Response(
                body=body,
                status=status,
            )

    return inner
