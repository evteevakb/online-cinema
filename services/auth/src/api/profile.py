from fastapi import APIRouter, Depends, status
from uuid import uuid4
from models.entity import User
from services.profile import ProfileService, get_profile_service
from openapi.user import UserResponse, UserUpdate, LoginHistoryResponse
from fastapi.responses import JSONResponse


router = APIRouter()


@router.get(
    '/{uuid}',
    response_model=UserResponse,
    summary="Профиль пользователя",
    description="Данные о пользователе",
)
async def get_profile_info(
    uuid: str,
    profile_service: ProfileService = Depends(get_profile_service),
) -> UserResponse:
    profile = await profile_service.get_profile_info(uuid)
    return profile


@router.post(
    '/{uuid}/reset/password',
    response_model=UserUpdate,
    summary="Поменять пароль.",
    description="Поменять пароль.",
)
async def reset_password(
    uuid: str,
    password: str,
    profile_service: ProfileService = Depends(get_profile_service),
) -> UserUpdate:
    await profile_service.reset_password(uuid, password)
    return JSONResponse(
        content={"message": "Password updated successfully"},
        status_code=status.HTTP_200_OK
    )


@router.post(
    '/{uuid}/reset/login',
    response_model=UserUpdate,
    summary="Поменять логин.",
    description="Поменять логин.",
)
async def reset_login(
    uuid: str,
    login: str,
    profile_service: ProfileService = Depends(get_profile_service),
) -> UserUpdate:
    await profile_service.reset_login(uuid, login)
    return JSONResponse(
        content={"message": "Login updated successfully"},
        status_code=status.HTTP_200_OK
    )


@router.get(
    '/{uuid}/history',
    response_model=LoginHistoryResponse,
    summary="Истоия лог-инов.",
    description="Получить историю вхождения в аккаунт пользователя.",
)
async def get_history(
    uuid: str,
    profile_service: ProfileService = Depends(get_profile_service),
) -> LoginHistoryResponse:
    return await profile_service.get_history(uuid)
