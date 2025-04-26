from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RoleInDb(BaseModel):
    name: str
    description: Optional[str]
    created_at: datetime
    modified_at: datetime

    class Config:
        from_attributes = True


class RoleCreateUpdate(BaseModel):
    name: str
    description: Optional[str]

class BaseRole(BaseModel):
    """Represents a role with a name."""

    name: str


class UserRole(BaseModel):
    """Represents a relationship between a user and a role."""

    user_uuid: UUID
    role: BaseRole
