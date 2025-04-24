"""
Role endpoints for the auth service.
"""

from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.request_models import UserRole
from db.postgre import get_session
from openapi.roles import AssignRole, RevokeRole
from services.role import get_role_service, RoleService
from services.user import get_user_service, UserService


router = APIRouter()


@router.patch(
    "/assign",
    summary=AssignRole.summary,
    description=AssignRole.description,
    response_description=AssignRole.response_description,
    responses=AssignRole.responses,
)
async def assign_role(
    data: UserRole,
    db: AsyncSession = Depends(get_session),
    role_service: RoleService = Depends(get_role_service),
    user_service: UserService = Depends(get_user_service),
) -> JSONResponse:
    user_uuid = data.user_uuid
    user = await user_service.get_user_with_roles(user_uuid=user_uuid)

    role_name = data.role.name
    role = await role_service.get_role(role_name)
    if role in user.roles:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"User with {user_uuid=} already has {role_name=}",
        )

    user.roles.append(role)
    await db.commit()
    return JSONResponse(
        content={
            "message": f"{role_name=} successfully assigned to user with {user_uuid=}"
        },
        status_code=HTTPStatus.OK,
    )


@router.patch(
    "/revoke",
    summary=RevokeRole.summary,
    description=RevokeRole.description,
    response_description=RevokeRole.response_description,
    responses=RevokeRole.responses,
)
async def revoke_role(
    data: UserRole,
    db: AsyncSession = Depends(get_session),
    role_service: RoleService = Depends(get_role_service),
    user_service: UserService = Depends(get_user_service),
) -> JSONResponse:
    user_uuid = data.user_uuid
    user = await user_service.get_user_with_roles(user_uuid=user_uuid)

    role_name = data.role.name
    role = await role_service.get_role(role_name)

    if role not in user.roles:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"User with {user_uuid=} does not have {role_name=}",
        )

    if len(user.roles) == 1:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Cannot revoke the last role from user with {user_uuid=}",
        )

    user.roles.remove(role)
    await db.commit()
    return JSONResponse(
        content={
            "message": f"{role_name=} successfully revoked from user with {user_uuid=}"
        },
        status_code=HTTPStatus.OK,
    )
