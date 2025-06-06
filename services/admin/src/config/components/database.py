"""
Contains database settings.
https://docs.djangoproject.com/en/5.1/ref/settings/#databases
"""

import os

from dotenv import load_dotenv

load_dotenv()


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", 5432),
        "OPTIONS": {"options": "-c search_path=public,content"},
    }
}
