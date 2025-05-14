from datetime import datetime, timedelta
from enum import Enum

from fastapi import Depends, HTTPException, status
from jose import jwt
from redis.asyncio import Redis
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgre import get_session
from db.redis import get_redis
from models.entity import (
    AuthEventType,
    LoginHistory,
    RefreshTokens,
    Role,
    User,
    UserRole
)
from schemas.auth import (
    LogoutResponse,
    TokenResponse,
    VerifyRequest,
    AuthorizationResponse,
)
from utils.fake_credentials import generate_username


class LoginTypes(str, Enum):
    STANDARD_LOGIN = 'standard_login'
    OAUTH_LOGIN = 'oauth_login'


class AuthService:
    def __init__(
        self,
        redis: Redis = Depends(get_redis),
        db: AsyncSession = Depends(get_session),
        secret_key: str = "your-secret-key",
        algorithm: str = "HS256",
        access_exp: int = 15,
        refresh_exp: int = 7 * 24,
    ):
        self.redis = redis
        self.db = db
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_exp = access_exp
        self.refresh_exp = refresh_exp

    def _create_token(self, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.now() + expires_delta
        to_encode.update({"exp": expire, "iat": datetime.now()})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def _create_access_token(self, user: User) -> str:
        return self._create_token(
            data={"sub": str(user.uuid), "email": user.email, "username": user.username},
            expires_delta=timedelta(minutes=self.access_exp),
        )

    async def _create_refresh_token(self, user: User) -> str:
        refresh_token = self._create_token(
            data={"sub": str(user.uuid), "email": user.email, "username": user.username},
            expires_delta=timedelta(minutes=self.refresh_exp),
        )
        await self._save_refresh_token(user.uuid, refresh_token)
        return refresh_token

    async def _save_refresh_token(self, user_uuid: str, token: str) -> None:
        token_entry = RefreshTokens(
            token=token,
            user_uuid=user_uuid,
            expires_at=datetime.now() + timedelta(days=self.refresh_exp / 24),
        )
        self.db.add(token_entry)
        await self.db.commit()

    async def register(
        self,
        password: str,
        username: str | None = None,
        email: str | None = None,
    ) -> TokenResponse:
        if username is None and email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either username or email must be provided.",
            )
        if username is None:
            username = generate_username()
        result = await self.db.execute(
            select(User).where(User.username == username, User.email == email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User already exists")

        role_result = await self.db.execute(select(Role).where(Role.name == "user"))
        user_role = role_result.scalar_one_or_none()

        if not user_role:
            user_role = Role(name="user")
            self.db.add(user_role)
            await self.db.commit()
            await self.db.refresh(user_role)

        user = User(username=username, email=email, password=password)
        user.is_active = True
        user.roles = [user_role]

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        access_token = self._create_access_token(user)
        refresh_token = await self._create_refresh_token(user)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def login(
        self,
        user_agent: str,
        username: str | None =  None,
        email: str | None = None,
        password: str | None = None,
        login_type: LoginTypes = LoginTypes.STANDARD_LOGIN
    ) -> TokenResponse:
        if username is None and email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either username or email must be provided.",
            )
        login_field = username or email

        result = await self.db.execute(
            select(User).where(
                (User.username == login_field) | (User.email == login_field)
            )
        )
        user = result.scalar_one_or_none()
        if not user or (login_type == LoginTypes.STANDARD_LOGIN and not user.check_password(password)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        result = await self.db.execute(
            select(RefreshTokens).where(RefreshTokens.user_uuid == user.uuid)
        )
        result = result.scalar_one_or_none()
        old_token = result.token if result else None
        if old_token:
            await self.db.execute(
                delete(RefreshTokens).where(RefreshTokens.token == old_token)
            )
            await self.db.commit()

        access_token = self._create_access_token(user)
        refresh_token = await self._create_refresh_token(user)

        login_event = LoginHistory(
            user_uuid=user.uuid,
            user_agent=user_agent,
            event_type=AuthEventType.LOGIN.value
        )
        self.db.add(login_event)
        await self.db.commit()

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def login_django(self, email: str, password: str, user_agent: str) -> AuthorizationResponse:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not user.check_password(password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        role_result = await self.db.execute(select(UserRole).where(UserRole.user_uuid == str(user.uuid)))
        user_role = role_result.scalar_one_or_none()
        user_roles = [user_role.role_name]

        login_event = LoginHistory(
            user_uuid=user.uuid,
            user_agent=user_agent,
            event_type=AuthEventType.LOGIN.value,
        )
        self.db.add(login_event)
        await self.db.commit()

        return AuthorizationResponse(
            user_uuid=str(user.uuid),
            email=user.email,
            first_name="",
            last_name="",
            is_staff=False,
            is_active=user.is_active,
            is_superuser=False,
            roles=[roles for roles in user_roles],
        )


    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        token_entry = await self.db.execute(
            select(RefreshTokens).where(RefreshTokens.token == refresh_token)
        )
        token = token_entry.scalar_one_or_none()

        if not token or token.expires_at < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        await self.db.execute(
            delete(RefreshTokens).where(RefreshTokens.token == refresh_token)
        )
        await self.db.commit()

        user = await self._get_user_by_id(str(token.user_uuid))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        access_token = self._create_access_token(user)
        new_refresh_token = await self._create_refresh_token(user)

        return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)

    async def logout(
        self, access_token: str, refresh_token: str, user_agent: str
    ) -> LogoutResponse:
        try:
            payload = jwt.decode(
                access_token, self.secret_key, algorithms=[self.algorithm]
            )
            exp_timestamp = payload.get("exp")
            user_uuid = payload.get("sub")  # Обычно ID пользователя

            cache_key = f"blacklist:{access_token}"
            invalidated_token = await self.redis.get(cache_key)
            if invalidated_token or not exp_timestamp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid access token",
                )

            expires_in = exp_timestamp - int(datetime.now().timestamp())
            if expires_in <= 0:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Access token has expired",
                )

            await self.redis.set(cache_key, "true", ex=expires_in)

        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token"
            )

        token_entry = await self.db.execute(
            select(RefreshTokens).where(RefreshTokens.token == refresh_token)
        )
        token = token_entry.scalar_one_or_none()

        if token:
            await self.db.execute(
                delete(RefreshTokens).where(RefreshTokens.token == refresh_token)
            )
            await self.db.commit()

        # Запись в login_history
        if user_uuid:
            logout_event = LoginHistory(
                user_uuid=user_uuid,
                user_agent=user_agent,
                event_type=AuthEventType.LOGOUT.value
            )
            self.db.add(logout_event)
            await self.db.commit()

        return LogoutResponse(detail="Successfully logged out")

    async def _get_user_by_id(self, user_id: str) -> User:
        result = await self.db.execute(select(User).where(User.uuid == user_id))
        return result.scalar_one_or_none()

    async def verify_access_token(self, data: VerifyRequest) -> dict:
        try:
            payload = jwt.decode(
                data.access_token, self.secret_key, algorithms=[self.algorithm]
            )
            exp_timestamp = payload.get("exp")

            cache_key = f"blacklist:{data.access_token}"
            invalidated_token = await self.redis.get(cache_key)
            if invalidated_token or not exp_timestamp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid access token",
                )

            expires_in = exp_timestamp - int(datetime.now().timestamp())
            if expires_in <= 0:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Access token has expired",
                )

        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token"
            )

        user = await self._get_user_by_id(payload.get("sub"))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return payload


def get_auth_service(
    redis: Redis = Depends(get_redis),
    postgres: AsyncSession = Depends(get_session),
) -> AuthService:
    return AuthService(redis=redis, db=postgres)
