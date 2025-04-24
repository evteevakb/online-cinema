"""
Contains mandatory methods for communication between the storage and the application
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from db.postgre import Base


ModelTypeT = TypeVar("ModelTypeT", bound=Base)


class BaseRepository(ABC):
    """Agreement which methods will be created to implement CRUD"""

    @abstractmethod
    async def read(
        self,
        session: Any,
        field_name: str,
        field_value: UUID | str,
        relationship: str | None = None,
    ):
        """Read method"""


class RepositoryDB(BaseRepository, Generic[ModelTypeT]):
    """Base class for working with a database"""

    def __init__(self, model: Type[ModelTypeT]):
        self._model = model

    async def read(
        self,
        session: AsyncSession,
        field_name: str,
        field_value: UUID | str,
        relationship: str | None = None,
    ) -> Optional[ModelTypeT]:
        statement = select(self._model).where(
            getattr(self._model, field_name) == field_value
        )
        if relationship:
            statement = statement.options(
                selectinload(getattr(self._model, relationship))
            )
        result = await session.execute(statement=statement)
        return result.scalar_one_or_none()
