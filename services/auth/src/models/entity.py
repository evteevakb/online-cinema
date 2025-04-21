import uuid
from datetime import datetime, timedelta

from sqlalchemy import Boolean, Column, String, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from werkzeug.security import check_password_hash, generate_password_hash

from db.constants import AUTH_SCHEMA
from db.postgre import Base


class BaseModel(Base):
    __abstract__ = True
    __table_args__ = {"schema": AUTH_SCHEMA}


class DateTimeBaseModel(BaseModel):
    __abstract__ = True

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified_at = Column(
        TIMESTAMP, nullable=False, onupdate=func.now(), server_default=func.now()
    )


class Role(DateTimeBaseModel):
    __tablename__ = "roles"

    name = Column(Text, unique=True, nullable=False)
    description = Column(Text)

    def __repr__(self) -> str:
        return f"<Role {self.name}>"


class User(DateTimeBaseModel):
    __tablename__ = "users"

    email = Column(Text, unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role_uuid = Column(UUID(as_uuid=True), ForeignKey(f"{AUTH_SCHEMA}.roles.uuid"))
    is_active = Column(Boolean, default=True, nullable=False)

    def __init__(self, password: str, email: str) -> None:
        self.email = email
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class LoginHistory(BaseModel):
    __tablename__ = "login_history"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_uuid = Column(UUID(as_uuid=True), ForeignKey(f"{AUTH_SCHEMA}.users.uuid"))
    user_agent = Column(Text)
    login_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class RefreshTokens(BaseModel):
    __tablename__ = "refresh_tokens"

    token = Column(Text, nullable=False, unique=True, primary_key=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey(f"{AUTH_SCHEMA}.users.uuid"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    expires_at = Column(
        TIMESTAMP, nullable=False, default=lambda: datetime.now() + timedelta(days=7)
    )
