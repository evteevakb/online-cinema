"""
Provides a utility function to generate fake usernames and passwords.
"""

import random
import secrets
import string

CHARACTERS_NUM = 16
PASSWORD_LENGTH = 16


def generate_username(
    random_part_length: int = CHARACTERS_NUM,
) -> str:
    """Generate a completely random fake username. The username is composed of a
        fixed prefix 'user_' and a random alphanumeric string (letters and digits).

    Args:
        random_part_length (int): Length of the random alphanumeric string.

    Returns:
        str: A randomly generated username.
    """
    random_string = "".join(
        random.choices(string.ascii_letters + string.digits, k=random_part_length)
    )
    return f"user_{random_string}"


def generate_password(
    length: int = PASSWORD_LENGTH,
) -> str:
    """Generate a random password.

    Args:
        length (int): Length of the password.

    Returns:
        str: A generated random password.
    """
    symbols = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(symbols) for _ in range(length))
