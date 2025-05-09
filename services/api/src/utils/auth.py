from enum import Enum
from typing import Any, List

from fastapi import Header, HTTPException
import httpx
from starlette import status

from core.config import APISettings
from schemas.auth import AuthorizationResponse, VerifyRequest, VerifyResponse

api_settings = APISettings()


class Roles(str, Enum):
    ADMIN = "admin"
    USER = "user"
    PAID_USER = "paid_user"
    SUPERUSER = "superuser"


class AuthorizationRequests:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def _get_request(
        self, url: str, method: str = "GET", data: dict | None = None
    ) -> Any:
        async with httpx.AsyncClient() as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Method not allowed",
                    )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code, detail=e.response.json()
                )
            except httpx.RequestError:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Authentication service unavailable",
                )

            data = response.json()
            return data

    async def get_user_roles(self, user_uuid: str) -> List[str]:
        try:
            if not user_uuid:
                return [Roles.USER]
            data = await self._get_request(
                f"http://{self.host}:{self.port}/api/v1/roles/user/{user_uuid}"
            )
            return data
        except HTTPException:
            return [Roles.USER]

    async def verify_access_token(self, access_token: str) -> VerifyResponse:
        try:
            data = await self._get_request(
                url=f"http://{self.host}:{self.port}/api/v1/auth/verify_access_token",
                method="POST",
                data=VerifyRequest(access_token=access_token).model_dump(),
            )
            return VerifyResponse(**data)
        except HTTPException:
            return VerifyResponse(sub="", email="", exp=0, iat=0)


class Authorization:
    def __init__(self, allowed_roles: List[Roles]):
        self.allowed_roles = allowed_roles
        self.request_class = AuthorizationRequests(
            host=api_settings.auth_host, port=api_settings.auth_port
        )

    async def __call__(self, authorization: str = Header(...)) -> AuthorizationResponse:
        token = self.extract_token(authorization)
        payload = await self.verify_token(token)

        user_uuid = payload.sub
        roles = await self.request_class.get_user_roles(user_uuid=user_uuid)

        if not any(role in roles for role in self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This operation is forbidden for you",
            )
        return AuthorizationResponse(user_uuid=user_uuid, roles=roles)

    @staticmethod
    def extract_token(authorization: str) -> str:
        """Берём токен из заголовка Authorization: Bearer <token>"""
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
            )
        return authorization[len("Bearer ") :]

    async def verify_token(self, token: str) -> VerifyResponse:
        payload = await self.request_class.verify_access_token(token)
        return payload
