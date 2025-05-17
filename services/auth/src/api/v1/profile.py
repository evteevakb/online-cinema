from typing import Any, cast

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter

from core.config import RateLimiterSettings
from openapi.user import GetHistory, GetProfileInfo, ResetLogin, ResetPassword
from schemas.auth import AuthorizationResponse
from schemas.user import PaginatedLoginHistoryResponse, UserResponse, UserUpdate
from services.profile import get_profile_service, ProfileService
from utils.auth import Authorization, Roles

router = APIRouter()
settings = RateLimiterSettings()


@router.get(
    "/{login}",
    response_model=UserResponse,
    summary=GetProfileInfo.summary,
    description=GetProfileInfo.description,
    response_description=GetProfileInfo.response_description,
    responses=cast(dict[int | str, dict[str, Any]], GetProfileInfo.responses),
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def get_profile_info(
    login: str,
    profile_service: ProfileService = Depends(get_profile_service),
) -> UserResponse:
    profile = await profile_service.get_profile_info(login)
    return profile


@router.post(
    "/{login}/reset/password",
    response_model=UserUpdate,
    summary=ResetPassword.summary,
    description=ResetPassword.description,
    response_description=ResetPassword.response_description,
    responses=cast(dict[int | str, dict[str, Any]], ResetPassword.responses),
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def reset_password(
    login: str,
    password: str,
    new_password: str,
    profile_service: ProfileService = Depends(get_profile_service),
) -> UserUpdate:
    await profile_service.reset_password(
        login=login, old_password=password, new_password=new_password
    )
    return JSONResponse(
        content={"message": "Password updated successfully"},
        status_code=status.HTTP_200_OK,
    )


@router.post(
    "/{login}/reset/login",
    response_model=UserUpdate,
    summary=ResetLogin.summary,
    description=ResetLogin.description,
    response_description=ResetLogin.response_description,
    responses=cast(dict[int | str, dict[str, Any]], ResetLogin.responses),
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def reset_login(
    login: str,
    new_login: str,
    password: str,
    profile_service: ProfileService = Depends(get_profile_service),
) -> UserUpdate:
    await profile_service.reset_login(
        login=login, new_login=new_login, password=password
    )
    return JSONResponse(
        content={"message": "Login updated successfully"},
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/{uuid}/history",
    response_model=PaginatedLoginHistoryResponse,
    summary=GetHistory.summary,
    description=GetHistory.description,
    response_description=GetHistory.response_description,
    responses=cast(dict[int | str, dict[str, Any]], ResetPassword.responses),
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def get_history(
    uuid: str,
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
    profile_service: ProfileService = Depends(get_profile_service),
    user_with_roles: AuthorizationResponse = Depends(
        Authorization(
            allowed_roles=[Roles.SUPERUSER, Roles.ADMIN, Roles.PAID_USER, Roles.USER]
        )
    ),
) -> PaginatedLoginHistoryResponse:
    return await profile_service.get_history(uuid, user_with_roles, page, size)
