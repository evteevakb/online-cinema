from pydantic import BaseModel

class VerifyRequest(BaseModel):
    access_token: str
    token_type: str = "bearer"

class VerifyResponse(BaseModel):
    sub: str
    email: str
    exp: int
    iat: int
