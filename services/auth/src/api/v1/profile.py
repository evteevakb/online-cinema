from typing import Any, cast, List

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from openapi.user import GetHistory, GetProfileInfo, ResetLogin, ResetPassword
from schemas.user import LoginHistoryResponse, UserResponse, UserUpdate
from schemas.auth import AuthorizationResponse
from services.profile import get_profile_service, ProfileService
from utils.auth import Authorization, Roles

router = APIRouter()


@router.get(
    "/{email}",
    response_model=UserResponse,
    summary=GetProfileInfo.summary,
    description=GetProfileInfo.description,
    response_description=GetProfileInfo.response_description,
    responses=cast(dict[int | str, dict[str, Any]], GetProfileInfo.responses),
)
async def get_profile_info(
    email: str,
    profile_service: ProfileService = Depends(get_profile_service),
) -> UserResponse:
    profile = await profile_service.get_profile_info(email)
    return profile


@router.post(
    "/{email}/reset/password",
    response_model=UserUpdate,
    summary=ResetPassword.summary,
    description=ResetPassword.description,
    response_description=ResetPassword.response_description,
    responses=cast(dict[int | str, dict[str, Any]], ResetPassword.responses),
)
async def reset_password(
    login: str,
    password: str,
    new_password: str,
    profile_service: ProfileService = Depends(get_profile_service),
) -> UserUpdate:
    await profile_service.reset_password(login, password, new_password)
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
)
async def reset_login(
    login: str,
    new_login: str,
    password: str,
    profile_service: ProfileService = Depends(get_profile_service),
) -> UserUpdate:
    await profile_service.reset_login(login, new_login, password)
    return JSONResponse(
        content={"message": "Login updated successfully"},
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/{uuid}/history",
    response_model=List[LoginHistoryResponse],
    summary=GetHistory.summary,
    description=GetHistory.description,
    response_description=GetHistory.response_description,
    responses=cast(dict[int | str, dict[str, Any]], ResetPassword.responses),
)
async def get_history(
    uuid: str,
    profile_service: ProfileService = Depends(get_profile_service),
    user_with_roles: AuthorizationResponse = Depends(
        Authorization(
            allowed_roles=[Roles.SUPERUSER, Roles.ADMIN, Roles.PAID_USER, Roles.USER]
        )
    ),
) -> List[LoginHistoryResponse]:
    return await profile_service.get_history(uuid, user_with_roles)
