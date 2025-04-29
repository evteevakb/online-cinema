"""
User role definitions for access control.
"""

from enum import Enum


class Roles(str, Enum):
    """Possible user roles."""
    ADMIN = "admin"
    USER = "user"
    PAID_USER = "paid_user"
    SUPERUSER = "superuser"


all_role_names = [role.value for role in Roles]
