"""
Token generation utilities for authentication during tests.
"""

from datetime import datetime, timedelta
from typing import Any

from jose import jwt

from models.entity import User
from settings import APISettings


settings = APISettings()


def create_access_token(user: User) -> Any:
    """Generate a JWT access token for the given user.

    Args:
        user (User): the user instance for whom the token is being generated.

    Returns:
        str: the encoded JWT access token.
    """
    return _create_token(
        data={"sub": str(user.uuid), "email": user.email},
        expires_delta=timedelta(minutes=settings.auth_access_exp),
    )


def _create_token(data: dict[str, Any], expires_delta: timedelta) -> Any:
    """Encode a JWT token with the given payload and expiration.

    Args:
        data (dict): the payload to encode in the token.
        expires_delta (timedelta): time delta after which the token should expire.

    Returns:
        str: the encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire, "iat": datetime.now()})
    return jwt.encode(
        to_encode, settings.auth_secret_key, algorithm=settings.auth_algorithm
    )
