from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api import health
from api.v1 import films, genres, persons
from core.config import APISettings, ElasticSettings, RedisSettings
from db import elastic, redis

api_settings = APISettings()
elastic_settings = ElasticSettings()
redis_settings = RedisSettings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(
        host=redis_settings.host,
        port=redis_settings.port,
        username=redis_settings.user_name,
        password=redis_settings.user_password,
    )
    elastic.es = AsyncElasticsearch(
        hosts=[f"http://{elastic_settings.host}:{elastic_settings.port}"],
        basic_auth=(
            elastic_settings.user,
            elastic_settings.password,
        ),
    )
    yield
    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    title=api_settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
