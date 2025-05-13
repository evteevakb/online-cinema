"""
Main application setup for the authentication service.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter
from redis.asyncio import Redis
from starlette.middleware.sessions import SessionMiddleware

from api import health
from api.v1 import auth, oauth, profile, roles
from core.config import APISettings, OAuthSessionSettings, RedisSettings
from core.tracing import add_tracer
from db import redis
from middlewares.request_middleware import AddIdentifierMiddleware, RequestIDMiddleware

api_settings = APISettings()
oauth_session_settings = OAuthSessionSettings()
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
    await FastAPILimiter.init(redis.redis)
    yield
    await redis.redis.close()


app = FastAPI(
    title=api_settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


app.add_middleware(RequestIDMiddleware)
app.add_middleware(AddIdentifierMiddleware)
app.add_middleware(SessionMiddleware, secret_key=oauth_session_settings.secret_key)

# tracer must be called strictly after middlewares
add_tracer(app)


app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(profile.router, prefix="/api/v1/profile", tags=["profile"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(oauth.router, prefix="/api/v1/oauth", tags=["oauth"])
