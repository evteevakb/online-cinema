import http
import json
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
import requests
from requests.exceptions import RequestException
from strenum import StrEnum

User = get_user_model()
logger = logging.getLogger(__name__)


class Roles(StrEnum):
    ADMIN = "admin"
    SUPERUSER = "superuser"


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = settings.AUTH_API_LOGIN_URL
        payload = {"email": username, "password": password}

        try:
            response = requests.post(url, data=json.dumps(payload), timeout=5)
            response.raise_for_status()
        except RequestException as e:
            logger.warning(f"Authentication request failed: {e}")
            return None

        try:
            data = response.json()
        except ValueError as e:
            logger.warning(f"Invalid JSON response: {e}")
            return None

        try:
            user, created = User.objects.get_or_create(
                id=data["user_uuid"],
            )
            user.email = data.get("email")
            user.first_name = data.get("first_name")
            user.last_name = data.get("last_name")
            user.is_staff = any(
                role in data.get("roles", []) for role in (Roles.ADMIN, Roles.SUPERUSER)
            )
            user.is_active = data.get("is_active")
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)

        except User.DoesNotExist:
            return None
