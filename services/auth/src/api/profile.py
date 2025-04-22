from fastapi import APIRouter, Depends
from uuid import uuid4
from models.entity import User
from services.profile import ProfileService, get_profile_service
from openapi.user import UserResponse, UserUpdate, LoginHistoryResponse


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
) -> User:
    profile = await profile_service.get_profile_info(uuid)
    return profile


@router.get(
    '/{uuid}/reset/password',
    response_model=UserUpdate,
    summary="Поменять пароль.",
    description="Поменять пароль.",
)
async def get_reset_password(
    uuid: str,
    password: str,
    profile_service: ProfileService = Depends(get_profile_service),
) -> User:
    return await profile_service.reset_password(uuid, password)


@router.get(
    '/{uuid}/reset/login',
    response_model=UserUpdate,
    summary="Поменять логин.",
    description="Поменять логин.",
)
async def get_reset_login(
    uuid: str,
    login: str,
    profile_service: ProfileService = Depends(get_profile_service),
) -> User:
    return await profile_service.reset_login(uuid, login)


@router.get(
    '/{uuid}/history',
    response_model=LoginHistoryResponse,
    summary="Истоия лог-инов.",
    description="Получить историю вхождения в аккаунт пользователя.",
)
async def get_get_history(
    uuid: str,
    profile_service: ProfileService = Depends(get_profile_service),
) -> User:
    return await profile_service.get_history(uuid)
