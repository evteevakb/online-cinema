"""
Contains service for user management.
"""

from http import HTTPStatus
from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgre import get_session
from models.entity import User
from services.storage import BaseRepository, RepositoryDB


class UserService:
    """Service for managing user."""

    def __init__(
        self,
        repository: BaseRepository,
        session: Any,
    ) -> None:
        self.repository = repository
        self.session = session

    async def get_user_with_roles(self, user_uuid: UUID):
        user_with_roles = await self.repository.read(
            session=self.session,
            field_name="uuid",
            field_value=user_uuid,
            relationship="roles",
        )
        if not user_with_roles:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"User with {user_uuid=} not found",
            )
        return user_with_roles


def get_user_service(
    session: AsyncSession = Depends(get_session),
) -> UserService:
    return UserService(
        repository=RepositoryDB(model=User),
        session=session,
    )
