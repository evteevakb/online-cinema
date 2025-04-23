"""
Role endpoints for the auth service.
"""

from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from api.v1.response_models import UserRole
from db.postgre import get_session
from models.entity import Role, User

# TODO: add OpenAPI

router = APIRouter()


@router.patch(
    "/assign",
)
async def assign_role(
    data: UserRole,
    db: AsyncSession = Depends(get_session)
) -> JSONResponse:
    user_uuid = data.user_uuid

    user = await db.execute(
        select(User)
        .where(User.uuid == user_uuid)
        .options(selectinload(User.roles))
    )
    user = user.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"User with {user_uuid=} not found",
            )

    role_name = data.role.name
    role = await db.get(Role, role_name)
    if not role:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Role with {role_name=} not found",
            )
    if role in user.roles:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"User with {user_uuid=} already has {role_name=}",
            )
    
    user.roles.append(role)
    await db.commit()
    return JSONResponse(
        content={"message": f"{role_name=} successfully assigned to user with {user_uuid=}"},
        status_code=HTTPStatus.OK,
    )


# @router.patch(
#     "/revoke",
# )
# async def revoke_role():
#     pass
