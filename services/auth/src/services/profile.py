from fastapi import Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from werkzeug.security import generate_password_hash

from db.postgre import get_session
from db.redis import get_redis
from models.entity import LoginHistory, User
from openapi.user import LoginHistoryResponse, UserResponse
from schemas.auth import AuthorizationResponse
from schemas.user import PaginatedLoginHistoryResponse
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

    async def get_profile_info(self, login: str) -> UserResponse:
        stmt = select(User).where((User.username == login) | (User.email == login))
        info = await self.postgres.execute(stmt)
        user = info.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return UserResponse.model_validate(user)

    async def get_history(
        self,
        user_uuid: str,
        user_with_roles: AuthorizationResponse,
        page: int,
        size: int,
    ) -> PaginatedLoginHistoryResponse:
        if user_with_roles.user_uuid != user_uuid and not any(
            role in self.SU_ROLES for role in user_with_roles.roles
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        try:
            data_query = (
                select(LoginHistory)
                .where(LoginHistory.user_uuid == user_uuid)
                .limit(size)
                .offset((page - 1) * size)
            )
            result = await self.postgres.execute(data_query)
            history = result.scalars().all()

            count_query = (
                select(func.count())
                .select_from(LoginHistory)
                .where(LoginHistory.user_uuid == user_uuid)
            )
            total_result = await self.postgres.execute(count_query)
            total = total_result.scalar_one()

            data = []
            for h in history:
                print(
                    f"Original item: {h}, Type: {type(h)}"
                )  # Выводим оригинальный элемент и его тип
                validated_item = LoginHistoryResponse.model_validate(
                    h
                )  # Применяем модель
                print(
                    f"Validated item: {validated_item}, Type: {type(validated_item)}"
                )  # Выводим результат и его тип
                data.append(validated_item)

            # Убедитесь, что total, page, size - целые числа
            print(f"Total: {total}, Page: {page}, Size: {size}")

            # Возвращаем структуру PaginatedLoginHistoryResponse
            return PaginatedLoginHistoryResponse(
                data=data,  # Список LoginHistoryResponse
                total=total,  # Целое число
                page=page,  # Целое число
                size=size,  # Целое число
            )

        except Exception as e:
            raise HTTPException(
                status_code=500, detail={"message": f"Ошибка базы данных: {str(e)}"}
            )

    async def reset_password(
        self, login: str, old_password: str, new_password: str
    ) -> None:
        stmt = select(User).where((User.username == login) | (User.email == login))
        result = await self.postgres.execute(stmt)
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

    async def reset_login(self, login: str, new_login: str, password: str) -> None:
        stmt = select(User).where((User.username == login) | (User.email == login))
        result = await self.postgres.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        elif user.check_password(password):
            if user.username == login:
                user.username = new_login
            else:
                user.email = new_login
            await self.postgres.commit()
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


def get_profile_service(
    redis: Redis = Depends(get_redis),
    postgres: AsyncSession = Depends(get_session),
) -> ProfileService:
    return ProfileService(redis, postgres)
