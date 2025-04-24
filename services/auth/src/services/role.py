"""
Contains service for role management.
"""

from http import HTTPStatus
from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgre import get_session
from models.entity import Role
from services.storage import BaseRepository, RepositoryDB


class RoleService:
    """Service for managing roles."""

    def __init__(
        self,
        repository: BaseRepository,
        session: Any,
    ) -> None:
        self.repository = repository
        self.session = session

    async def get_role(self, role_name: str):
        role = await self.repository.read(
            session=self.session,
            field_name="name",
            field_value=role_name,
        )
        if not role:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Role with {role_name=} not found",
            )
        return role


def get_role_service(
    session: AsyncSession = Depends(get_session),
) -> RoleService:
    return RoleService(
        repository=RepositoryDB(model=Role),
        session=session,
    )
