from typing import List

from pydantic import BaseModel


class VerifyRequest(BaseModel):
    access_token: str
    token_type: str = "bearer"


class VerifyResponse(BaseModel):
    sub: str
    exp: int
    iat: int
    email: str | None
    username: str | None


class AuthorizationResponse(BaseModel):
    user_uuid: str
    roles: List[str]
