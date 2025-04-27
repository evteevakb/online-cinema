"""
OpenAPI schema definitions for the profile endpoint.
"""

from pydantic import BaseModel, field_validator
from datetime import datetime
from uuid import UUID


class UserResponse(BaseModel):
    """Schema for user response."""

    uuid: str
    email: str
    created_at: datetime
    is_active: bool

    @field_validator("uuid", mode="before")
    def convert_uuid_to_str(cls, value):
        if isinstance(value, UUID):
            return str(value)
        return value

    class Config:
        from_attributes = True


class LoginHistoryResponse(BaseModel):
    """Schema for login history response."""

    id: int
    user_uuid: int
    login_time: datetime
    ip_address: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema to return when updating user."""

    email: str | None = None
