"""
Main application setup for the authentication service.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api import health
from api.v1 import auth, profile, roles
from core.config import APISettings, RedisSettings
from db import redis

api_settings = APISettings()
redis_settings = RedisSettings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI lifespan context manager."""
    redis.redis = Redis(
        host=redis_settings.host,
        port=redis_settings.port,
        username=redis_settings.user_name,
        password=redis_settings.user_password,
    )
    yield
    await redis.redis.close()


app = FastAPI(
    title=api_settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(profile.router, prefix="/api/v1/profile", tags=["profile"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])
