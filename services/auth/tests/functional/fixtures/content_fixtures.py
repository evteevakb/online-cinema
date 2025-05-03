"""
Provides fixtures for roles and users management.
"""

from typing import Callable

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models.entity import Role, User


@pytest_asyncio.fixture(name="create_roles")
async def create_roles(db_session: AsyncSession) -> Callable[[list[str]], None]:
    """Fixture for creating roles."""

    async def inner(roles: list[str]) -> None:
        """Create roles in the database if they do not exist.

        Args:
            roles (List[str]): list of role names to create.
        """
        result = await db_session.execute(select(Role.name))
        existing_roles = {row[0] for row in result.all()}
        missing_roles = [role for role in roles if role not in existing_roles]

        for role_name in missing_roles:
            role = Role(name=role_name, description=f"Default {role_name} role")
            db_session.add(role)

        if missing_roles:
            await db_session.commit()

    return inner


@pytest_asyncio.fixture(name="create_user")
async def create_user(
    db_session: AsyncSession,
    create_roles: Callable,
) -> Callable[[str, str, list[str]], User]:
    """Fixture for creating a user with specific roles."""

    async def inner(
        email: str,
        password: str,
        role_names: list[str],
    ) -> User:
        """Create a user with the specified roles.

        Args:
            email (str): the email of the user.
            password (str): the password of the user.
            role_names (List[str]): list of role names to assign to the user.

        Retruns:
            User: the created user object.
        """
        await create_roles(role_names)
        user = User(email=email, password=password)

        result = await db_session.execute(select(Role).where(Role.name.in_(role_names)))
        roles = result.scalars().all()
        user.roles = roles
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return inner


@pytest_asyncio.fixture(name="get_user")
def get_user(db_session: AsyncSession) -> Callable[[str], User]:
    """Fixture for getting a user by UUID."""

    async def inner(user_uuid: str) -> User:
        """Get a user by UUID.

        Args:
            user_uuid (str): the UUID of the user to retrieve.

        Returns:
            User: the user object if found, otherwise None.
        """
        result = await db_session.execute(
            select(User).where(User.uuid == user_uuid).options(selectinload(User.roles))
        )
        return result.scalar_one_or_none()

    return inner
