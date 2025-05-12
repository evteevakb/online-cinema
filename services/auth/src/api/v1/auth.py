from fastapi import APIRouter, Depends, Request
from fastapi_limiter.depends import RateLimiter

from core.config import RateLimiterSettings
from schemas.auth import (
    LogoutResponse,
    TokenResponse,
    VerifyRequest,
    VerifyResponse,
    AuthorizationResponse,
)
from schemas.auth import (
    RegisterRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
    VerifyRequest,
    VerifyResponse,
)
from services.auth import AuthService, get_auth_service

router = APIRouter()
settings = RateLimiterSettings()




@router.post("/registration", response_model=TokenResponse)
async def register_user(
    data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await auth_service.register(data.email, data.password)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    user_agent = request.headers.get("user-agent", "unknown")
    return await auth_service.login(data.email, data.password, user_agent)

@router.post("/login_django", response_model=AuthorizationResponse)
async def login(
    data: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthorizationResponse:
    user_agent = request.headers.get("user-agent", "unknown")
    return await auth_service.login_django(data.email, data.password, user_agent)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await service.refresh_tokens(data.refresh_token)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    data: LogoutRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> LogoutResponse:
    user_agent = request.headers.get("user-agent", "unknown")
    return await auth_service.logout(data.access_token, data.refresh_token, user_agent)
