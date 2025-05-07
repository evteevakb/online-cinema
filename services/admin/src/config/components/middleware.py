import os

from django.conf import settings
from dotenv import load_dotenv

load_dotenv()


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if settings.DEBUG:
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

allowed_hosts = os.getenv("ALLOWED_HOSTS")
if allowed_hosts is None:
    ALLOWED_HOSTS = []
else:
    ALLOWED_HOSTS = allowed_hosts.split(",")

INTERNAL_IPS = [
    "127.0.0.1",
]
