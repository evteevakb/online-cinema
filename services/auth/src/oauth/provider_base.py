from abc import ABC, abstractmethod
from typing import Any

from schemas.auth import OAuthResponse
from starlette.responses import RedirectResponse


class BaseProvider(ABC):
    """Abstract class for implementing OAuth 2.0 providers."""

    @abstractmethod
    def get_redirect_url(self) -> RedirectResponse:
        """Generates the URL to redirect the user to the authorization page.

        Returns:
            str: URL to redirect the user to the authorization page.
        """
        pass

    @abstractmethod
    async def callback(self) -> dict[str, Any]:
        """Handles the response from the provider after the user is authorized.

        Returns:
            dict: Tokens received after a successful authorization.
        """
        pass

    @abstractmethod
    def authorize(self) -> OAuthResponse:
        """Authorizes the user via the provider.

        # Returns:
        #     dict: User information received from the provider.
        """
        pass