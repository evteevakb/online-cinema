"""Add user_social_accounts table

Revision ID: 06e3dc0d51e9
Revises: 656357d18cd3
Create Date: 2025-05-10 19:31:06.169770

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

from db.constants import AUTH_SCHEMA
from models.entity import User
from utils.fake_credentials import generate_username

# revision identifiers, used by Alembic.
revision: str = "06e3dc0d51e9"
down_revision: Union[str, None] = "656357d18cd3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users", sa.Column("username", sa.String(length=255)), schema=AUTH_SCHEMA
    )
    connection = op.get_bind()
    session = Session(bind=connection)
    users = session.query(User).filter(User.username.is_(None)).all()
    for user in users:
        user.username = generate_username()
    session.commit()
    op.alter_column("users", "username", nullable=False, schema=AUTH_SCHEMA)
    op.create_unique_constraint(
        "uq_users_username", "users", ["username"], schema=AUTH_SCHEMA
    )
    op.alter_column(
        "users", "email", existing_type=sa.Text(), nullable=True, schema=AUTH_SCHEMA
    )

    op.create_table(
        "user_social_accounts",
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column("user_uuid", sa.UUID(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("social_id", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "modified_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("provider", "social_id", name="uq_provider_social_id"),
        sa.ForeignKeyConstraint(
            ["user_uuid"],
            ["auth.users.uuid"],
        ),
        schema=AUTH_SCHEMA,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_users_username", "users", type_="unique", schema=AUTH_SCHEMA)
    op.drop_column("users", "username", schema=AUTH_SCHEMA)
    op.alter_column(
        "users", "email", existing_type=sa.Text(), nullable=False, schema=AUTH_SCHEMA
    )

    op.drop_table("user_social_accounts", schema=AUTH_SCHEMA)
