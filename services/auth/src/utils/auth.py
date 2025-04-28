from enum import Enum
from typing import List, Any

import httpx
from fastapi import HTTPException, Header
from starlette import status

from schemas.auth import VerifyRequest, VerifyResponse


class Roles(str, Enum):
    ADMIN = "admin"
    USER = "user"
    PAID_USER = "paid_user"
    SUPERUSER = "superuser"

class AuthorizationRequests:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def _get_request(self, url: str, method: str = 'GET', data: dict = None) -> Any:
        async with httpx.AsyncClient() as client:
            try:
                if method.upper() == 'GET':
                    response = await client.get(url)
                elif method.upper() == 'POST':
                    response = await client.post(url, json=data)
                else:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Method not allowed")
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
            except httpx.RequestError:
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authentication service unavailable")

            data = response.json()
            return data

    async def get_user_roles(self, user_uuid: str) -> List[str]:
        data = await self._get_request(f"http://{self.host}:{self.port}/api/v1/roles/user/{user_uuid}")
        return data

    async def verify_access_token(self, access_token: str) -> VerifyResponse:
        data = await self._get_request(
            url=f"http://{self.host}:{self.port}/api/v1/auth/verify_access_token",
            method='POST',
            data=VerifyRequest(access_token=access_token).model_dump()
        )
        return data


class Authorization:
    def __init__(self, allowed_roles: List[Roles]):
        self.allowed_roles = allowed_roles
        self.request_class = AuthorizationRequests(host='localhost', port=8000)

    async def __call__(self, authorization: str = Header(...)):
        token = self.extract_token(authorization)
        payload = await self.verify_token(token)

        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user_uuid",
            )

        roles = await self.request_class.get_user_roles(user_uuid=user_uuid)

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

    async def verify_token(self, token: str) -> dict:
        payload = await self.request_class.verify_access_token(token)
        return payload