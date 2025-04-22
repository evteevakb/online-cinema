from fastapi import APIRouter, Depends
from uuid import uuid4
from src.models import User
from services.profile import ProfileService, get_profile_service

router = APIRouter()


@router.get(
    '/{uuid}',
    response_model=User,
    summary="Профиль пользователя",
    description="Данные о пользователе",
)
def get_profile_info(
    uuid: int,
    profile_service: ProfileService = Depends(get_profile_service),
) -> User:
    profile = await profile_service.get_profile_info(uuid)
    return profile


@router.get(
    '/{uuid}/reset/password',
    response_model=User,
    summary="Поменять пароль.",
    description="Поменять пароль.",
)
def get_reset_password(
    uuid: int,
    password: str,
    profile_service: ProfileService = Depends(get_profile_service),
) -> User:
    return await profile_service.reset_password(uuid, password)


@router.get(
    '/{uuid}/reset/login',
    response_model=User,
    summary="Поменять логин.",
    description="Поменять логин.",
)
def get_reset_login(
    uuid: int,
    login: str,
    profile_service: ProfileService = Depends(get_profile_service),
) -> User:
    return await profile_service.reset_login(uuid, login)


@router.get(
    '/{uuid}/history',
    response_model=User,
    summary="Истоия лог-инов.",
    description="Получить историю вхождения в аккаунт пользователя.",
)
def get_get_history(
    uuid: int,
    profile_service: ProfileService = Depends(get_profile_service),
) -> User:
    return await profile_service.get_history(uuid)
