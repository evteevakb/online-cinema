from fastapi import APIRouter, Depends
from schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    LogoutRequest,
    LogoutResponse,
    VerifyRequest,
    VerifyResponse
)
from services.auth import AuthService, get_auth_service


router = APIRouter()


@router.post(
    "/registration",
    response_model=TokenResponse,
)
async def register_user(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.register(user_data)


@router.post("/login")
async def login(
        data: UserLogin,
        auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.login(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
        refresh_token: str,
        service: AuthService = Depends(get_auth_service)
):
    return await service.refresh_tokens(refresh_token)

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    data: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.logout(data)


@router.post('/verify_access_token', response_model=VerifyResponse)
async def verify_access_token(
    data: VerifyRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> VerifyResponse:
    return await auth_service.verify_access_token(data)