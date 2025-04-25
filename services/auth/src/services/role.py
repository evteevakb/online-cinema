"""
Contains service for role management.
"""

from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgre import get_session
from models.entity import Role
from schemas.entity import RoleCreateUpdate


class RoleService:
    """Service for managing roles."""

    def __init__(
        self,
        session: Any,
    ) -> None:
        self.session = session

    async def get_role(self, role_name: str):
        stmt = select(Role).filter_by(name=role_name)
        result = await self.session.execute(stmt)
        role = result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=404, detail='Role not found')
        return role

    async def get_roles(self, skip: int = 0, limit: int = 0):
        stmt = select(Role).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        roles = list(result.scalars())
        return roles

    async def create_role(self, role_create: RoleCreateUpdate):
        role = Role(**role_create.dict())
        try:
            self.session.add(role)
            await self.session.commit()
            await self.session.refresh(role)
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Role {role_create.name} already exists"
            )
        return role

    async def update_role(self, role_name: str, role_update: RoleCreateUpdate):
        stmt = update(Role).filter_by(name=role_name).values(
            name=role_update.name,
            description=role_update.description
        ).returning(Role)
        result = await self.session.execute(stmt)
        await self.session.commit()
        updated_role = result.scalar_one_or_none()
        if not updated_role:
            raise HTTPException(status_code=404, detail="Role not found")
        return updated_role

    async def delete_role(self, role_name: str):
        stmt = delete(Role).filter_by(name=role_name).returning(Role.name)
        result = await self.session.execute(stmt)
        deleted = result.scalar_one_or_none()
        if not deleted:
            raise HTTPException(status_code=404, detail='Role not found')
        await self.session.commit()


def get_role_service(
    session: AsyncSession = Depends(get_session),
) -> RoleService:
    return RoleService(
        session=session,
    )