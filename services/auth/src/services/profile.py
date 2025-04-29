import uuid
from typing import List

from fastapi import Depends, HTTPException, status
from openapi.user import LoginHistoryResponse, UserResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.postgre import get_session
from db.redis import get_redis
from models.entity import LoginHistory, User


class ProfileService:
    def __init__(
        self, redis: Redis = Depends(get_redis),
        postgres: AsyncSession = Depends(get_session)
    ):
        self.redis = redis
        self.postgres = postgres

    async def get_profile_info(self, uuid_: str) -> UserResponse:
        try:
            profile_uuid = uuid.UUID(uuid_)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found"
            )
        stmt = select(User).where(User.uuid == profile_uuid)
        info = await self.postgres.execute(stmt)
        user = info.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
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

    async def reset_password(self, email: str, old_password: str, new_password: str) -> None:
        result = await self.postgres.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        elif user.check_password(old_password):
            user.password = new_password
            await self.postgres.commit()
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    async def reset_login(self, email: str, new_login: str, password: str) -> None:
        result = await self.postgres.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        elif user.check_password(password):
            user.email = new_login
            await self.postgres.commit()
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


def get_profile_service(
        redis: Redis = Depends(get_redis),
        postgres: AsyncSession = Depends(get_session),
) -> ProfileService:
    return ProfileService(redis, postgres)
