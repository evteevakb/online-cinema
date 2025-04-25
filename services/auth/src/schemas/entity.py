from datetime import datetime
from typing import Optional

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
