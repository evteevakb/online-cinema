"""
API fixtures for functional tests.
"""

from typing import Any, AsyncGenerator, Awaitable, Callable

import aiohttp
import pytest_asyncio
from pydantic import BaseModel

from settings import APISettings


api_settings = APISettings()


class Response(BaseModel):
    """Represents a HTTP response object."""

    body: list[dict[str, Any]] | dict[str, Any]
    status: int


@pytest_asyncio.fixture(name="session", scope="session")
async def session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    """Provides a shared aiohttp client session for all tests in the session.

    Yields:
        aiohttp.ClientSession: an asynchronous HTTP client session.
    """
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name="make_get_request")
def make_get_request(
    session: aiohttp.ClientSession,
) -> Callable[[str, dict[str, Any] | None], Awaitable[Response]]:
    """Fixture for making GET requests to the API.

    Args:
        session (aiohttp.ClientSession): the shared client session.

    Returns:
        Callable: an async function to perform GET requests.
    """

    async def inner(
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> Response:
        params = params or {}
        url = api_settings.base_url + endpoint
        async with session.get(url, params=params) as response:
            return Response(
                body=await response.json(),
                status=response.status,
            )

    return inner
