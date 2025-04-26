from fastapi import APIRouter, Depends, HTTPException, status
from services.auth import UserRegister, UserLogin, TokenResponse
from services.auth import AuthService, get_auth_service
from async_fastapi_jwt_auth import AuthJWT
from models.auth import AuthJWTSettings
from fastapi import Query

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

@router.post("/logout")
async def logout(
    refresh_token: str = Query(...),
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.logout(refresh_token)