from typing import List

from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class VerifyRequest(BaseModel):
    access_token: str
    token_type: str = "bearer"


class VerifyResponse(BaseModel):
    sub: str
    email: str
    exp: int
    iat: int


class LogoutResponse(BaseModel):
    detail: str


class AuthorizationResponse(BaseModel):
    user_uuid: str
    roles: List[str]


class SocialUserData(BaseModel):
    social_id: str
    email: EmailStr | None = None
