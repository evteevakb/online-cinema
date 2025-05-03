from fastapi import APIRouter, Depends, Request

from schemas.auth import (
    LogoutResponse,
    TokenResponse,
    VerifyRequest,
    VerifyResponse,
)
from services.auth import AuthService, get_auth_service

router = APIRouter()


@router.post(
    "/registration",
    response_model=TokenResponse,
)
async def register_user(
    email: str,
    password: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await auth_service.register(email, password)


@router.post("/login", response_model=TokenResponse)
async def login(
    email: str,
    password: str,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    user_agent = request.headers.get("user-agent", "unknown")
    return await auth_service.login(email, password, user_agent)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str, service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    return await service.refresh_tokens(refresh_token)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    access_token: str,
    refresh_token: str,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> LogoutResponse:
    user_agent = request.headers.get("user-agent", "unknown")
    return await auth_service.logout(access_token, refresh_token, user_agent)


@router.post("/verify_access_token", response_model=VerifyResponse)
async def verify_access_token(
    data: VerifyRequest, auth_service: AuthService = Depends(get_auth_service)
) -> VerifyResponse:
    return await auth_service.verify_access_token(data)
