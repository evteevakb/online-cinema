from enum import Enum

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.postgre import get_session
from models.entity import User, UserSocialAccount
from services.auth import AuthService, get_auth_service
from utils.fake_credentials import generate_password, generate_username


class Provider(str, Enum):
    GOOGLE: str = "google"
    YANDEX: str = "yandex"


class OAuthService:
    def __init__(
        self,
        db_session: AsyncSession,
        auth_service: AuthService,
    ) -> None:
        self.db_session = db_session
        self.auth_service = auth_service

    async def get_user(
        self,
        social_id: str,
        provider: Provider,
        email: str | None,
    ) -> User:
        stmt = (
            select(UserSocialAccount)
            .where(UserSocialAccount.social_id == social_id)
            .options(selectinload(UserSocialAccount.user))
        )
        user_social_account = await self.db_session.execute(stmt)
        user_social_account = user_social_account.scalar_one_or_none()
        user = user_social_account.user if user_social_account else None
        if not user_social_account:
            username = generate_username()
            password = generate_password()
            _ = await self.auth_service.register(
                username=username,
                email=email,
                password=password,
            )
            user = await self.db_session.execute(
                select(User).where(User.username == username, User.email == email)
            )
            user = user.scalar_one()
            user_social_account = UserSocialAccount(
                user_uuid=user.uuid,
                social_id=social_id,
                provider=provider,
                user=user,
            )

            self.db_session.add(user_social_account)
            await self.db_session.commit()
            await self.db_session.refresh(user_social_account)
        return user


def get_oauth_service(
    db_session: AsyncSession = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> OAuthService:
    return OAuthService(
        db_session=db_session,
        auth_service=auth_service,
    )
