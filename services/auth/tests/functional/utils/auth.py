from datetime import datetime, timedelta

from jose import jwt

from models.entity import User
from settings import APISettings


settings = APISettings()


def create_access_token(user: User) -> str:
    return _create_token(
        data={"sub": str(user.uuid), "email": user.email},
        expires_delta=timedelta(minutes=settings.auth_access_exp),
        )
    

def _create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire, "iat": datetime.now()})
    return jwt.encode(to_encode, settings.auth_secret_key, algorithm=settings.auth_algorithm)
