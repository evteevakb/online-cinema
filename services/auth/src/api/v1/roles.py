from typing import List
from fastapi import APIRouter, Depends

from schemas.entity import RoleInDb, RoleCreateUpdate
from db.postgre import get_session
from models.entity import Role
from services.role import RoleService, get_role_service

router = APIRouter()


@router.get(
    path='',
    response_model=List[RoleInDb]
)
async def list_roles(
        skip: int = 0,
        limit: int = 10,
        role_service: RoleService = Depends(get_role_service)
) -> List[RoleInDb]:
    roles = await role_service.get_roles(skip, limit)
    return roles


@router.get(
    path='/{role_name}',
    response_model=RoleInDb
)
async def get_role(role_name: str, role_service: RoleService = Depends(get_role_service)) -> RoleInDb:
    role = await role_service.get_role(role_name)
    return role


@router.post(
    path='',
    response_model=RoleInDb
)
async def create_role(
        role_create: RoleCreateUpdate,
        role_service: RoleService = Depends(get_role_service)
) -> RoleInDb:
    role_created = await role_service.create_role(role_create)
    return role_created


@router.put(
    path='/{role_name}',
    response_model=RoleInDb
)
async def update_role(role_name: str,
                      role_update: RoleCreateUpdate,
                      role_service: RoleService = Depends(get_role_service)
                      ) -> RoleInDb:
    updated_role = await role_service.update_role(role_name, role_update)
    return updated_role


@router.delete(
    path='/{role_name}'
)
async def delete_role(role_name: str, role_service: RoleService = Depends(get_role_service)) -> dict:
    await role_service.delete_role(role_name)
    return {'message': f'Role {role_name} deleted'}
