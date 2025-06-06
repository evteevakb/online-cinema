"""
OpenAPI schema definitions for the profile endpoint.
"""

from datetime import datetime
from typing import Any, List
from uuid import UUID

from pydantic import BaseModel, field_validator


class UserResponse(BaseModel):
    """Schema for user response."""

    uuid: str
    created_at: datetime
    is_active: bool
    email: str | None = None
    username: str | None = None

    @field_validator("uuid", mode="before")
    def convert_uuid_to_str(cls, value: str | UUID) -> str:
        if isinstance(value, UUID):
            return str(value)
        return value

    class Config:
        from_attributes = True


class LoginHistoryResponse(BaseModel):
    """Schema for login history response."""

    uuid: str
    user_uuid: str
    event_type: str
    user_agent: str | None
    occurred_at: datetime

    @field_validator("uuid", "user_uuid", "event_type", mode="before")
    def convert_to_str(cls, value: Any) -> str:
        return str(value)

    class Config:
        from_attributes = True


class PaginatedLoginHistoryResponse(BaseModel):
    data: List[LoginHistoryResponse]
    total: int
    page: int
    size: int


class UserUpdate(BaseModel):
    """Schema to return when updating user."""

    login: str | None = None
