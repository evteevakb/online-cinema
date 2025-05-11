from datetime import datetime, timedelta
import enum
import uuid

from sqlalchemy import Boolean, Column, ForeignKey, func, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import relationship
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


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(Text, unique=True, nullable=False, primary_key=True)
    description = Column(Text)
    users = relationship(
        "User",
        secondary=f"{AUTH_SCHEMA}.user_roles",
        back_populates="roles",
        passive_deletes=True,
    )
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified_at = Column(
        TIMESTAMP, nullable=False, onupdate=func.now(), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Role {self.name}>"


class UserRole(BaseModel):
    __tablename__ = "user_roles"

    user_uuid = Column(
        UUID(as_uuid=True), ForeignKey(f"{AUTH_SCHEMA}.users.uuid"), primary_key=True
    )
    role_name = Column(
        Text,
        ForeignKey(f"{AUTH_SCHEMA}.roles.name", ondelete="CASCADE"),
        primary_key=True,
    )


class User(DateTimeBaseModel):
    __tablename__ = "users"

    username = Column(String(255), unique=True, nullable=False)
    email = Column(Text, unique=True, nullable=True)
    password = Column(String(255), nullable=False)
    roles = relationship(
        "Role", secondary=f"{AUTH_SCHEMA}.user_roles", back_populates="users"
    )
    social_accounts = relationship("UserSocialAccount", back_populates="user")
    is_active = Column(Boolean, default=True, nullable=False)

    def __init__(self, password: str, email: str) -> None:
        self.email = email
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class UserSocialAccount(DateTimeBaseModel):
    __tablename__ = "user_social_accounts"
    __table_args__ = (
        UniqueConstraint("provider", "social_id", name="uq_provider_social_id"),
        {"schema": AUTH_SCHEMA},
    )

    user_uuid = Column(
        UUID(as_uuid=True), ForeignKey(f"{AUTH_SCHEMA}.users.uuid"), primary_key=True
    )
    provider = Column(String(50), nullable=False)
    social_id = Column(String(255), nullable=False)
    user = relationship("User", back_populates="social_accounts")


class AuthEventType(enum.Enum):
    LOGIN = "login"
    LOGOUT = "logout"


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
    event_type = Column(Text, nullable=False)
    occurred_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class RefreshTokens(BaseModel):
    __tablename__ = "refresh_tokens"

    token = Column(Text, nullable=False, unique=True, primary_key=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey(f"{AUTH_SCHEMA}.users.uuid"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    expires_at = Column(
        TIMESTAMP, nullable=False, default=lambda: datetime.now() + timedelta(days=7)
    )
