"""
OpenAPI schema definitions for role assignment and revocation endpoints.
"""

import datetime
from http import HTTPStatus
from typing import Any, ClassVar

from pydantic import BaseModel

from schemas.role import RoleInDb


__all__ = ["AssignRole", "ListRole", "RevokeRole"]

role_name = "user"
user_uuid = "68039548-01c4-800b-babf-fff7ac5fb54e"


class _UserNotFoundExample:
    """NOT_FOUND response example for missing users."""

    example: ClassVar[dict[str, Any]] = {
        "summary": "User not found",
        "value": {"detail": f"User with {user_uuid=} not found"},
    }


class _RoleNotFoundExample:
    """NOT_FOUND response example for missing roles."""

    example: ClassVar[dict[str, Any]] = {
        "summary": "Role not found",
        "value": {"detail": f"Role with {role_name=} not found"},
    }


class AssignRole(BaseModel):
    """OpenAPI schema for the role assignment endpoint."""

    summary: ClassVar[str] = "Assign role"
    description: ClassVar[str] = (
        "Assigns a role to the specified user if not already assigned."
    )
    response_description: ClassVar[str] = (
        "Confirmation that the role has been assigned."
    )
    responses: ClassVar[dict[int, Any]] = {
        HTTPStatus.OK: {
            "description": "Request completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": f"{role_name=} successfully assigned to user with {user_uuid=}"
                    }
                }
            },
        },
        HTTPStatus.BAD_REQUEST: {
            "description": "Invalid request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": f"User with {user_uuid=} already has {role_name=}"
                    }
                }
            },
        },
        HTTPStatus.NOT_FOUND: {
            "description": "User or role not found",
            "content": {
                "application/json": {
                    "examples": {
                        "User not found": _UserNotFoundExample.example,
                        "Role not found": _RoleNotFoundExample.example,
                    }
                }
            },
        },
    }


class RevokeRole(BaseModel):
    """OpenAPI schema for the role revocation endpoint."""

    summary: ClassVar[str] = "Revoke role"
    description: ClassVar[str] = (
        "Revokes a role from the specified user, unless it's their last role."
    )
    response_description: ClassVar[str] = "Confirmation that the role has been revoked."
    responses: ClassVar[dict[int, Any]] = {
        HTTPStatus.OK: {
            "description": "Request completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": f"{role_name=} successfully revoked from user with {user_uuid=}"
                    }
                }
            },
        },
        HTTPStatus.BAD_REQUEST: {
            "description": "Invalid request",
            "content": {
                "application/json": {
                    "examples": {
                        "Role not assigned": {
                            "summary": "Role not assigned",
                            "value": {
                                "detail": f"User with {user_uuid=} does not have {role_name=}"
                            },
                        },
                        "Last role": {
                            "summary": "Last role",
                            "value": {
                                "detail": f"Cannot revoke the last role from user with {user_uuid=}"
                            },
                        },
                    }
                }
            },
        },
        HTTPStatus.NOT_FOUND: {
            "description": "User or role not found",
            "content": {
                "application/json": {
                    "examples": {
                        "User not found": _UserNotFoundExample.example,
                        "Role not found": _RoleNotFoundExample.example,
                    }
                }
            },
        },
    }


class _RoleResponseContent(BaseModel):
    example: ClassVar[list[RoleInDb]] = [
        RoleInDb(
            name="admin",
            description="It is admin",
            created_at=datetime.datetime(year=2025, month=1, day=1),
            modified_at=datetime.datetime(year=2025, month=1, day=1),
        ),
        RoleInDb(
            name="user",
            description="Just user",
            created_at=datetime.datetime(year=2025, month=1, day=1),
            modified_at=datetime.datetime(year=2025, month=1, day=1),
        ),
    ]


class ListRole(BaseModel):
    """OpenAPI schema for the list role endpoint."""

    summary: ClassVar[str] = "List roles"
    description: ClassVar[str] = "List all roles"
    response_description: ClassVar[str] = "List of all roles from db"
    responses: ClassVar[dict[int, Any]] = {
        HTTPStatus.OK: {
            "description": "Request completed successfully",
            "content": {"application/json": {"example": _RoleResponseContent.example}},
        }
    }
