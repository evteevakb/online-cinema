from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from redis.asyncio import Redis
from db.postgre import get_session
from db.redis import get_redis
from models.entity import User, RefreshTokens
from models.auth import UserRegister, UserLogin, TokenResponse
from datetime import datetime, timedelta
from jose import jwt
from uuid import uuid4


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
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def _create_access_token(self, user: User) -> str:
        return self._create_token(
            data={
                "sub": str(user.uuid),
                "email": user.email,
                # "role": user.role,
            },
            expires_delta=timedelta(minutes=self.access_exp),
        )

    async def _create_refresh_token(self, user: User) -> str:
        refresh_token = str(uuid4())
        await self._save_refresh_token(user.uuid, refresh_token)
        return refresh_token

    async def _save_refresh_token(self, user_uuid: str, token: str):
        await self.db.execute(
            delete(RefreshTokens).where(RefreshTokens.user_uuid == user_uuid)
        )
        token_entry = RefreshTokens(
            token=token,
            user_uuid=user_uuid,
            expires_at=datetime.utcnow() + timedelta(days=self.refresh_exp)
        )
        self.db.add(token_entry)
        await self.db.commit()

    async def _save_access_token(self, user_uuid: str, token: str):
        await self.redis.set(
            f"access:{user_uuid}",
            token,
            ex=timedelta(minutes=self.access_exp)
        )

    async def register(self, user_data: UserRegister) -> TokenResponse:
        result = await self.db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User already exists")

        user = User(email=user_data.email, password=user_data.password)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        access_token = self._create_access_token(user)
        refresh_token = await self._create_refresh_token(user)
        await self._save_access_token(str(user.uuid), access_token)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def login(self, credentials: UserLogin) -> TokenResponse:
        result = await self.db.execute(select(User).where(User.email == credentials.email))
        user = result.scalar_one_or_none()
        if not user or not user.check_password(credentials.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        await self.db.execute(
            delete(RefreshTokens).where(RefreshTokens.user_uuid == user.uuid)
        )

        access_token = self._create_access_token(user)
        refresh_token = await self._create_refresh_token(user)
        await self._save_access_token(str(user.uuid), access_token)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        token_entry = await self.db.execute(
            select(RefreshTokens).where(RefreshTokens.token == refresh_token)
        )
        token = token_entry.scalar_one_or_none()

        if not token or token.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        await self.db.execute(delete(RefreshTokens).where(RefreshTokens.token == refresh_token))

        user = await self._get_user_by_id(str(token.user_uuid))
        access_token = self._create_access_token(user)
        new_refresh_token = await self._create_refresh_token(user)

        await self._save_access_token(str(user.uuid), access_token)

        return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)

    async def logout(self, refresh_token: str = Query(...)):
        token_entry = await self.db.execute(
            select(RefreshTokens).where(RefreshTokens.token == refresh_token)
        )
        token = token_entry.scalar_one_or_none()

        if not token:
            raise HTTPException(status_code=404, detail="Refresh token not found")

        await self.db.execute(
            delete(RefreshTokens).where(RefreshTokens.token == refresh_token)
        )
        await self.db.commit()

        await self.redis.delete(f"access:{token.user_uuid}")

        return {"detail": "Successfully logged out"}

    async def _get_user_by_id(self, user_id: str) -> User:
        result = await self.db.execute(select(User).where(User.uuid == user_id))
        return result.scalar_one_or_none()


def get_auth_service(
    redis: Redis = Depends(get_redis),
    postgres: AsyncSession = Depends(get_session),
) -> AuthService:
    return AuthService(redis=redis, db=postgres)