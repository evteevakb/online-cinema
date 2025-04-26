from enum import Enum
from typing import List

import httpx
from fastapi import HTTPException, Header
from starlette import status


class Roles(str, Enum):
    ADMIN = "admin"
    USER = "user"
    SUPERUSER = "superuser"


async def get_user_roles(host: str, port: int, user_uuid: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"http://{host}:{port}/api/v1/roles/user/{user_uuid}"
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Authentication service error")
        except httpx.RequestError:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authentication service unavailable")

        data = response.json()
        return data


class Authorization:
    def __init__(self, allowed_roles: List[Roles]):
        self.allowed_roles = allowed_roles

    async def __call__(self, authorization: str = Header(...)):
        token = self.extract_token(authorization)
        payload = self.verify_token(token)

        user_uuid = payload.get("user")
        if not user_uuid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user_uuid",
            )

        roles = await get_user_roles(host='localhost', port=8000, user_uuid=user_uuid)

        if not any(role in roles for role in self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This operation is forbidden for you",
            )
        return roles

    @staticmethod
    def extract_token(authorization: str) -> str:
        """Берём токен из заголовка Authorization: Bearer <token>"""
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
            )
        return authorization[len("Bearer "):]

    def verify_token(self, token: str) -> dict:
        payload = {'user': 'd50e1a82-abd1-4fb7-9b3d-b471e249bf22',
                   "iat": 1201692377,
                   "exp": 1516239022,
                   } # MOCK
        return payload