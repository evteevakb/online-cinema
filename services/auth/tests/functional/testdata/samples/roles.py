from enum import Enum


class Roles(str, Enum):
    ADMIN = "admin"
    USER = "user"
    PAID_USER = "paid_user"
    SUPERUSER = "superuser"


all_role_names = [role.value for role in Roles]
