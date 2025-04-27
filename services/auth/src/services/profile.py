from fastapi import Depends, HTTPException, status
from models.entity import User, LoginHistory
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.postgre import get_session
from db.redis import get_redis
from typing import List
from openapi.user import UserResponse, UserUpdate, LoginHistoryResponse
import uuid


class ProfileService:
    def __init__(
        self, redis: Redis = Depends(get_redis),
        postgres: AsyncSession = Depends(get_session)
    ):
        self.redis = redis
        self.postgres = postgres

    async def get_profile_info(self, uuid_: str) -> UserResponse:
        profile_uuid = uuid.UUID(uuid_)
        stmt = select(User).where(User.uuid == profile_uuid)
        info = await self.postgres.execute(stmt)
        user = info.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse.model_validate(user)

    async def get_history(self, user_uuid: str) -> List[LoginHistoryResponse]:
        try:
            result = await self.postgres.execute(
                select(LoginHistory)
                .where(LoginHistory.user_uuid == user_uuid)
            )
            history = result.scalars().all()
            if not history:
                return []
            return [LoginHistoryResponse.model_validate(h) for h in history]

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={"message": f"Database error: {str(e)}"}
            )

    async def reset_password(self, user_uuid: str, new_password: str) -> None:
        result = await self.postgres.execute(
            select(User).where(User.uuid == user_uuid)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user.password = new_password
        await self.postgres.commit()

    async def reset_login(self, user_uuid: str, login: str) -> None:
        result = await self.postgres.execute(
            select(User).where(User.uuid == user_uuid)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user.email = login
        await self.postgres.commit()


def get_profile_service(
        redis: Redis = Depends(get_redis),
        postgres: AsyncSession = Depends(get_session),
) -> ProfileService:
    return ProfileService(redis, postgres)
