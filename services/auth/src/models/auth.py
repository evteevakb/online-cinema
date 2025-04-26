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


class AuthJWTSettings(BaseModel):
    authjwt_secret_key: str = "your-secret-key"
    authjwt_algorithm: str = "HS256"
    authjwt_access_token_expires: int = 15 * 60
