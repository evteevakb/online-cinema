from fastapi import APIRouter, Depends, Request
from fastapi_limiter.depends import RateLimiter

from core.config import RateLimiterSettings
from schemas.auth import (
    AuthorizationResponse,
    LoginRequest,
    LogoutRequest,
    LogoutResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    VerifyRequest,
    VerifyResponse,
)
from services.auth import AuthService, get_auth_service

router = APIRouter()
settings = RateLimiterSettings()


@router.post(
    "/registration",
    response_model=TokenResponse,
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def register_user(
    password: str,
    email: str = None,
    username: str = None,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await auth_service.register(
        email=email, password=password, username=username
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def login(
    password: str,
    request: Request,
    email: str = None,
    username: str = None,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    user_agent = request.headers.get("user-agent", "unknown")
    return await auth_service.login(
        email=email, password=password, user_agent=user_agent, username=username
    )


@router.post("/login_django", response_model=AuthorizationResponse)
async def login(
    data: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthorizationResponse:
    user_agent = request.headers.get("user-agent", "unknown")
    return await auth_service.login_django(data.email, data.password, user_agent)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def refresh_token(
    refresh_token: str,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await service.refresh_tokens(refresh_token)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def logout(
    access_token: str,
    refresh_token: str,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> LogoutResponse:
    user_agent = request.headers.get("user-agent", "unknown")
    return await auth_service.logout(access_token, refresh_token, user_agent)


@router.post(
    "/verify_access_token",
    response_model=VerifyResponse,
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def verify_access_token(
    data: VerifyRequest, auth_service: AuthService = Depends(get_auth_service)
) -> VerifyResponse:
    return await auth_service.verify_access_token(data)
