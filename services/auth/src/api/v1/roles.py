"""
Role endpoints for the auth service.
"""

from typing import Annotated, Any, cast, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi_limiter.depends import RateLimiter

from core.config import RateLimiterSettings
from openapi.roles import AssignRole, ListRole, RevokeRole
from schemas.auth import AuthorizationResponse
from schemas.role import RoleCreateUpdate, RoleInDb, UserRole
from services.role import get_role_service, RoleService
from utils.auth import Authorization, Roles

router = APIRouter()
settings = RateLimiterSettings()


@router.patch(
    "/assign",
    summary=AssignRole.summary,
    description=AssignRole.description,
    response_description=AssignRole.response_description,
    responses=cast(dict[int | str, dict[str, Any]], AssignRole.responses),
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def assign_role(
    data: UserRole,
    role_service: RoleService = Depends(get_role_service),
    _: AuthorizationResponse = Depends(
        Authorization(allowed_roles=[Roles.ADMIN, Roles.SUPERUSER])
    ),
) -> dict[str, str]:
    """Assign a role to a user.

    Args:
        data (UserRole): an object containing the user's UUID and the role to assign.
        role_service (RoleService): a service for role management.

    Returns:
        A message indicating the successfull result of the operation.
    """
    return await role_service.assign_role(
        user_uuid=data.user_uuid,
        role_name=data.role.name,
    )


@router.patch(
    "/revoke",
    summary=RevokeRole.summary,
    description=RevokeRole.description,
    response_description=RevokeRole.response_description,
    responses=cast(dict[int | str, dict[str, Any]], RevokeRole.responses),
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def revoke_role(
    data: UserRole,
    role_service: RoleService = Depends(get_role_service),
    _: AuthorizationResponse = Depends(
        Authorization(allowed_roles=[Roles.ADMIN, Roles.SUPERUSER])
    ),
) -> dict[str, str]:
    """Revoke a role from a user.

    Args:
        data (UserRole): an object containing the user's UUID and the role to revoke.
        role_service (RoleService):  a service for role management.

    Returns:
        A message indicating the successfull result of the operation.
    """
    return await role_service.revoke_role(
        user_uuid=data.user_uuid,
        role_name=data.role.name,
    )


@router.get(
    path="/user/{user_uuid}",
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def get_user_roles(
    user_uuid: UUID, role_service: RoleService = Depends(get_role_service)
) -> List[str]:
    return await role_service.get_user_roles(user_uuid=user_uuid)


@router.get(
    path="",
    response_model=List[RoleInDb],
    summary=ListRole.summary,
    description=ListRole.description,
    response_description=ListRole.response_description,
    responses=ListRole.responses,
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def list_roles(
    skip: Annotated[int, Query(description="Number of items to skip", ge=0)] = 0,
    limit: Annotated[int, Query(description="Pagination page size", ge=1)] = 10,
    role_service: RoleService = Depends(get_role_service),
) -> List[RoleInDb]:
    roles = await role_service.get_roles(skip, limit)
    return roles


@router.get(
    path="/{role_name}",
    response_model=RoleInDb,
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def get_role(
    role_name: str,
    role_service: RoleService = Depends(get_role_service),
    _: AuthorizationResponse = Depends(Authorization(allowed_roles=[Roles.SUPERUSER])),
) -> RoleInDb:
    role = await role_service.get_role(role_name)
    return role


@router.post(
    path="",
    response_model=RoleInDb,
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def create_role(
    role_create: RoleCreateUpdate,
    role_service: RoleService = Depends(get_role_service),
    _: AuthorizationResponse = Depends(Authorization(allowed_roles=[Roles.SUPERUSER])),
) -> RoleInDb:
    role_created = await role_service.create_role(role_create)
    return role_created


@router.put(
    path="/{role_name}",
    response_model=RoleInDb,
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def update_role(
    role_name: str,
    role_update: RoleCreateUpdate,
    role_service: RoleService = Depends(get_role_service),
    _: AuthorizationResponse = Depends(Authorization(allowed_roles=[Roles.SUPERUSER])),
) -> RoleInDb:
    updated_role = await role_service.update_role(role_name, role_update)
    return updated_role


@router.delete(
    path="/{role_name}",
    dependencies=[Depends(RateLimiter(times=settings.times, seconds=settings.seconds))],
)
async def delete_role(
    role_name: str,
    role_service: RoleService = Depends(get_role_service),
    _: AuthorizationResponse = Depends(Authorization(allowed_roles=[Roles.SUPERUSER])),
) -> dict:
    await role_service.delete_role(role_name)
    return {"message": f"Role {role_name} deleted"}
