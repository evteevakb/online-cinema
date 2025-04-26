"""
Contains service for role management.
"""
from http import HTTPStatus
from uuid import UUID
from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.engine import Result
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.postgre import get_session
from schemas.role import RoleCreateUpdate
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

    async def get_role(self, role_name: str) -> Role:
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

    async def get_roles(self, skip: int = 0, limit: int = 0) -> List[Role]:
        """Retrieve a list of roles with optional pagination.

        Args:
            skip (int): Number of roles to skip.
            limit (int): Maximum number of roles to return.

        Returns:
            List[Role]: List of role objects.
        """
        stmt = select(Role).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        roles = list(result.scalars())
        return roles

    async def create_role(self, role_create: RoleCreateUpdate) -> Role:
        """Create a new role.

        Args:
            role_create (RoleCreateUpdate): Data required to create a role.

        Returns:
            Role: The newly created role object.

        Raises:
            HTTPException: If the role already exists (500).
        """
        role = Role(**role_create.dict())
        try:
            self.session.add(role)
            await self.session.commit()
            await self.session.refresh(role)
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Role {role_create.name} already exists"
            )
        return role

    async def update_role(self, role_name: str, role_update: RoleCreateUpdate) -> Role:
        """Update an existing role.

        Args:
            role_name (str): The name of the role to update.
            role_update (RoleCreateUpdate): New values for the role.

        Returns:
            Role: The updated role object.

        Raises:
            HTTPException: If the role does not exist (404).
        """
        stmt = update(Role).filter_by(name=role_name).values(
            name=role_update.name,
            description=role_update.description
        ).returning(Role)
        result = await self.session.execute(stmt)
        await self.session.commit()
        updated_role = result.scalar_one_or_none()
        if not updated_role:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")
        return updated_role

    async def delete_role(self, role_name: str) -> None:
        """Delete a role by its name.

        Args:
            role_name (str): The name of the role to delete.

        Raises:
            HTTPException: If the role does not exist (404).
        """
        stmt = delete(Role).filter_by(name=role_name).returning(Role.name)
        result = await self.session.execute(stmt)
        deleted = result.scalar_one_or_none()
        if not deleted:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Role not found')
        await self.session.commit()

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

    async def get_user_roles(self, user_uuid: UUID) -> List[str]:
        user = await self.get_user_with_roles(user_uuid=user_uuid)
        roles_list = [role.name for role in user.roles]
        return roles_list

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
