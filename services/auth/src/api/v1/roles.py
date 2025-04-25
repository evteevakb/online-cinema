"""
Role endpoints for the auth service.
"""

from typing import Any, cast

from fastapi import APIRouter, Depends

from api.v1.request_models import UserRole
from openapi.roles import AssignRole, RevokeRole
from services.role import get_role_service, RoleService


router = APIRouter()


@router.patch(
    "/assign",
    summary=AssignRole.summary,
    description=AssignRole.description,
    response_description=AssignRole.response_description,
    responses=cast(dict[int | str, dict[str, Any]], AssignRole.responses),
)
async def assign_role(
    data: UserRole,
    role_service: RoleService = Depends(get_role_service),
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
)
async def revoke_role(
    data: UserRole,
    role_service: RoleService = Depends(get_role_service),
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
