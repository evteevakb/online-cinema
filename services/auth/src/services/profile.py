import uuid
from typing import List

from fastapi import Depends, HTTPException, status
from openapi.user import LoginHistoryResponse, UserResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from werkzeug.security import generate_password_hash

from db.postgre import get_session
from db.redis import get_redis
from models.entity import LoginHistory, User
from schemas.auth import AuthorizationResponse
from utils.auth import Roles


class ProfileService:
    SU_ROLES = [Roles.ADMIN, Roles.SUPERUSER]

    def __init__(
        self,
        redis: Redis = Depends(get_redis),
        postgres: AsyncSession = Depends(get_session),
    ):
        self.redis = redis
        self.postgres = postgres

    async def get_profile_info(self, email: str) -> UserResponse:
        stmt = select(User).where(User.email == email)
        info = await self.postgres.execute(stmt)
        user = info.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return UserResponse.model_validate(user)

    async def get_history(
        self, user_uuid: str, user_with_roles: AuthorizationResponse
    ) -> List[LoginHistoryResponse]:
        if user_with_roles.user_uuid != user_uuid and not any(
            role in self.SU_ROLES for role in user_with_roles.roles
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        try:
            result = await self.postgres.execute(
                select(LoginHistory).where(LoginHistory.user_uuid == user_uuid)
            )
            history = result.scalars().all()
            if not history:
                return []
            return [LoginHistoryResponse.model_validate(h) for h in history]

        except Exception as e:
            raise HTTPException(
                status_code=500, detail={"message": f"Database error: {str(e)}"}
            )

    async def reset_password(
        self, email: str, old_password: str, new_password: str
    ) -> None:
        result = await self.postgres.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        elif user.check_password(old_password):
            user.password = generate_password_hash(new_password)
            await self.postgres.commit()
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    async def reset_login(self, email: str, new_login: str, password: str) -> None:
        result = await self.postgres.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
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
