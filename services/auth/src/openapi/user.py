"""
OpenAPI schema definitions for the profile endpoint.
"""

from pydantic import BaseModel
from datetime import datetime


class UserResponse(BaseModel):
    """Schema for user response."""

    uuid: int
    email: str
    created_at: datetime
    is_active: bool

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
