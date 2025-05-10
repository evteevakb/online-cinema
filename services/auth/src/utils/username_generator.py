"""
Provides a utility function to generate fake usernames.
"""

import random
import string

CHARACTERS_NUM = 16


def generate_fake_username() -> str:
    """Generate a completely random fake username. The username is composed of a
        fixed prefix 'user_' and a random alphanumeric string (letters and digits).

    Returns:
        str: A randomly generated username.
    """
    random_string = "".join(
        random.choices(string.ascii_letters + string.digits, k=CHARACTERS_NUM)
    )
    return f"user_{random_string}"
