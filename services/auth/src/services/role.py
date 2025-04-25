"""
Contains service for role management.
"""

from http import HTTPStatus
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from db.postgre import get_session
from models.entity import Role, User


class RoleService:
    """Service for managing roles."""

    def __init__(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Initialize the RoleService.

        Args:
            db_session (AsyncSession): SQLAlchemy async session for database operations.
        """
        self.session = db_session

    async def get_user_with_roles(
        self,
        user_uuid: UUID,
    ) -> User:
        """Retrieve a user along with their roles.

        Args:
            user_uuid (UUID): unique identifier of the user.

        Returns:
            User: the user object with roles loaded.

        Raises:
            HTTPException (404): if the user does not exist.
        """
        result: Result[tuple[User]] = await self.session.execute(
            select(User).where(User.uuid == user_uuid).options(selectinload(User.roles))
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"User with {user_uuid=} not found",
            )
        return user

    async def get_role(
        self,
        role_name: str,
    ) -> Role:
        """Retrieve a role by its name.

        Args:
            role_name (str): the name of the role.

        Returns:
            Role: the role object.

        Raises:
            HTTPException (404): if the role does not exist.
        """
        role = await self.session.get(Role, role_name)
        if role is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Role with {role_name=} not found",
            )
        return role

    async def assign_role(
        self,
        user_uuid: UUID,
        role_name: str,
    ) -> dict[str, str]:
        """Assign a role to a user.

        Args:
            user_uuid (UUID): unique identifier of the user.
            role_name (str): name of the role to assign.

        Returns:
            dict[str, str]: a message confirming the role assignment.

        Raises:
            HTTPException (400): if the user already has the role.
        """
        user = await self.get_user_with_roles(user_uuid=user_uuid)
        role = await self.get_role(role_name=role_name)

        if role in user.roles:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"User with {user_uuid=} already has {role_name=}",
            )
        user.roles.append(role)
        await self.session.commit()
        return {
            "message": f"{role_name=} successfully assigned to user with {user_uuid=}"
        }

    async def revoke_role(
        self,
        user_uuid: UUID,
        role_name: str,
    ) -> dict[str, str]:
        """Revoke a role from a user.

        Args:
            user_uuid (UUID): unique identifier of the user.
            role_name (str): name of the role to revoke.

        Returns:
            dict[str, str]: a message confirming the role revocation.

        Raises:
            HTTPException (400): if the user does not have the role,
                or if it's the user's only role.
        """
        user = await self.get_user_with_roles(user_uuid=user_uuid)
        role = await self.get_role(role_name=role_name)

        if role not in user.roles:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"User with {user_uuid=} does not have {role_name=}",
            )

        if len(user.roles) == 1:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Cannot revoke the last role from user with {user_uuid=}",
            )

        user.roles.remove(role)
        await self.session.commit()
        return {
            "message": f"{role_name=} successfully revoked from user with {user_uuid=}"
        }


def get_role_service(db_session: AsyncSession = Depends(get_session)) -> RoleService:
    """Dependency injection provider for RoleService.

    Args:
        db_session (AsyncSession): SQLAlchemy async session.

    Returns:
        RoleService: an instance of the RoleService.
    """
    return RoleService(
        db_session=db_session,
    )
