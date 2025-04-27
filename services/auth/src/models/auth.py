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

class LogoutRequest(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class LogoutResponse(BaseModel):
    detail: str
