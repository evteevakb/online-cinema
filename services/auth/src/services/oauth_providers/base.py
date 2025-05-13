"""
Abstract base class for OAuth providers.
"""

from abc import ABC, abstractmethod
from typing import Any

from fastapi import Request

from core.config import OAuthBaseSettings
from schemas.auth import SocialUserData, TokenResponse
from services.auth import AuthService
from services.oauth import OAuthService


class BaseProvider(ABC):
    """Abstract class for implementing OAuth 2.0 providers."""

    provider_name: str

    @abstractmethod
    def __init__(
        self,
        settings: OAuthBaseSettings,
    ) -> None:
        """Initialize the provider with the corresponding OAuth settings.

        Args:
            settings: The provider-specific OAuth configuration.
        """

    @abstractmethod
    async def get_redirect_url(
        self,
        request: Request,
    ) -> Any:
        """Generate the URL to redirect the user to the provider's authorization page.

        Args:
            request: The incoming HTTP request.

        Returns:
            Any: A redirect response pointing to the provider's auth endpoint.
        """

    @abstractmethod
    async def get_user_info(
        self,
        request: Request,
    ) -> SocialUserData:
        """Retrieve user information from the provider using the authorization code.

        Args:
            request: The incoming HTTP request containing query parameters.

        Returns:
            SocialUserData: User attributes (e.g., email, name).
        """

    @abstractmethod
    async def authorize(
        self,
        request: Request,
        auth_service: AuthService,
        oauth_service: OAuthService,
    ) -> TokenResponse:
        """Authorize the user within the application using the provider's user info.

        Args:
            request: The incoming HTTP request.
            auth_service: The internal authentication service used to issue application tokens.
            oauth_service: The service used to manage users with social accounts.

        Returns:
            TokenResponse: Tokens representing the authenticated user session.
        """
