from typing import List, cast, Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from schemas.user import LoginHistoryResponse, UserResponse, UserUpdate
from openapi.user import GetProfileInfo, GetHistory, ResetPassword, ResetLogin
from services.profile import ProfileService, get_profile_service

router = APIRouter()


@router.get(
    '/{uuid}',
    response_model=UserResponse,
    summary=GetProfileInfo.summary,
    description=GetProfileInfo.description,
    response_description=GetProfileInfo.response_description,
    responses=cast(dict[int | str, dict[str, Any]], GetProfileInfo.responses),
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
    summary=ResetPassword.summary,
    description=ResetPassword.description,
    response_description=ResetPassword.response_description,
    responses=cast(dict[int | str, dict[str, Any]], ResetPassword.responses),
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
    summary=ResetLogin.summary,
    description=ResetLogin.description,
    response_description=ResetLogin.response_description,
    responses=cast(dict[int | str, dict[str, Any]], ResetLogin.responses),
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
    response_model=List[LoginHistoryResponse],
    summary=GetHistory.summary,
    description=GetHistory.description,
    response_description=GetHistory.response_description,
    responses=cast(dict[int | str, dict[str, Any]], ResetPassword.responses),
)
async def get_history(
    uuid: str,
    profile_service: ProfileService = Depends(get_profile_service),
) -> List[LoginHistoryResponse]:
    return await profile_service.get_history(uuid)
