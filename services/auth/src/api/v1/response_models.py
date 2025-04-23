from uuid import UUID

from pydantic import BaseModel


class BaseRole(BaseModel):
    name: str


class UserRole(BaseModel):
    user_uuid: UUID
    role: BaseRole
