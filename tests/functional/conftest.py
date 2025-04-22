import asyncio
import datetime
import uuid

import aiohttp
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from redis.asyncio import Redis

from tests.functional.settings import test_settings


@pytest_asyncio.fixture(name='redis_client')
async def redis_client() -> None:
    # host = "http://" + test_settings.redis_host
    redis = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    yield redis
    await redis.set(test_settings.es_index, datetime.datetime.now().isoformat())
    await redis.publish(test_settings.es_index, f"{test_settings.es_index} updated")
    await redis.aclose()

