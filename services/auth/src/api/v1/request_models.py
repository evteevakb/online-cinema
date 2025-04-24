"""
Data models for handling requests.
"""

from uuid import UUID

from pydantic import BaseModel


class BaseRole(BaseModel):
    """Represents a role with a name."""

    name: str


class UserRole(BaseModel):
    """Represents a relationship between a user and a role."""

    user_uuid: UUID
    role: BaseRole
