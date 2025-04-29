from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from jose import jwt
from redis.asyncio import Redis
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgre import get_session
from db.redis import get_redis
from models.entity import User, RefreshTokens
from schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    LogoutRequest,
    LogoutResponse,
    VerifyRequest,
)


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
            data={"sub": str(user.uuid), "email": user.email},
            expires_delta=timedelta(minutes=self.access_exp),
        )

    async def _create_refresh_token(self, user: User) -> str:
        refresh_token = self._create_token(
            data={"sub": str(user.uuid), "email": user.email},
            expires_delta=timedelta(minutes=self.refresh_exp),
        )
        await self._save_refresh_token(user.uuid, refresh_token)
        return refresh_token

    async def _save_refresh_token(self, user_uuid: str, token: str):
        token_entry = RefreshTokens(
            token=token,
            user_uuid=user_uuid,
            expires_at=datetime.now() + timedelta(days=self.refresh_exp / 24),
        )
        self.db.add(token_entry)
        await self.db.commit()

    async def register(self, user_data: UserRegister) -> TokenResponse:
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User already exists")

        user = User(email=user_data.email, password=user_data.password)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        access_token = self._create_access_token(user)
        refresh_token = await self._create_refresh_token(user)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def login(self, credentials: UserLogin) -> TokenResponse:
        result = await self.db.execute(
            select(User).where(User.email == credentials.email)
        )
        user = result.scalar_one_or_none()
        if not user or not user.check_password(credentials.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token = self._create_access_token(user)
        refresh_token = await self._create_refresh_token(user)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

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
        self, logout_request: LogoutRequest
    ) -> LogoutResponse:
        access_token = logout_request.access_token
        refresh_token = logout_request.refresh_token

        try:
            payload = jwt.decode(
                access_token, self.secret_key, algorithms=[self.algorithm]
            )
            exp_timestamp = payload.get("exp")

            cache_key = f"blacklist:{access_token}"
            invalidated_token = await self.redis.get(cache_key)
            if invalidated_token or not exp_timestamp:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

            expires_in = exp_timestamp - int(datetime.now().timestamp())

            if expires_in <= 0:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token has expired")

            await self.redis.set(cache_key, "true", ex=expires_in)

        except jwt.JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

        token_entry = await self.db.execute(
            select(RefreshTokens).where(RefreshTokens.token == refresh_token)
        )
        token = token_entry.scalar_one_or_none()

        if token:
            await self.db.execute(
                delete(RefreshTokens).where(RefreshTokens.token == refresh_token)
            )
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
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

            expires_in = exp_timestamp - int(datetime.now().timestamp())
            if expires_in <= 0:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token has expired")

        except jwt.JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

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
