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
    exp: int
    iat: int
    email: str | None
    username: str | None


class LogoutResponse(BaseModel):
    detail: str


class AuthorizationResponse(BaseModel):
    user_uuid: str
    email: str
    first_name: str
    is_staff: bool
    is_active: bool
    is_superuser: bool
    last_name: str
    roles: List[str]

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    access_token: str
    refresh_token: str


class SocialUserData(BaseModel):
    social_id: str
    email: EmailStr | None = None
