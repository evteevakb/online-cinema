from typing import List, Optional

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


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


class LogoutRequest(BaseModel):
    access_token: str
    refresh_token: str
    user_agent: Optional[str] = "unknown"


class LogoutResponse(BaseModel):
    detail: str


class AuthorizationResponse(BaseModel):
    user_uuid: str
    roles: List[str]
