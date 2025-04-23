from fastapi import Depends, HTTPException
from models.entity import User, LoginHistory
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.postgre import get_session
from db.redis import get_redis
from typing import List
from openapi.user import UserResponse, UserUpdate, LoginHistoryResponse


class ProfileService:
    def __init__(
        self, redis: Redis = Depends(get_redis),
        postgres: AsyncSession = Depends(get_session)
    ):
        self.redis = redis
        self.postgres = postgres

    async def get_profile_info(self, uuid: str) -> UserResponse:
        info = await self.postgres.execute(select(User).filter(User.uuid == uuid))
        user = info.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse.model_validate(user)

    async def get_history(self, uuid: str) -> List[LoginHistoryResponse]:
        info = await self.postgres.execute(select(LoginHistory).filter(LoginHistory.user_uuid == uuid))
        history = info.scalars().all()
        if history is None:
            raise HTTPException(status_code=404, detail="User not found")
        return [LoginHistoryResponse.model_validate(record) for record in history]

    async def reset_password(self, uuid: str, password: str) -> UserUpdate:
        info = await self.postgres.execute(select(User).filter(User.uuid == uuid))
        user = info.scalar_one_or_none()
        if user is not None:
            user.password = password
            return user
        raise HTTPException(status_code=404, detail="User not found")

    async def reset_login(self, uuid: str, login: str) -> UserUpdate:
        info = await self.postgres.execute(select(User).filter(User.uuid == uuid))
        user = info.scalar_one_or_none()
        if user is not None:
            user.email = login
            return user
        raise HTTPException(status_code=404, detail="User not found")


def get_profile_service(
        redis: Redis = Depends(get_redis),
        postgres: AsyncSession = Depends(get_session),
) -> ProfileService:
    return ProfileService(redis, postgres)
