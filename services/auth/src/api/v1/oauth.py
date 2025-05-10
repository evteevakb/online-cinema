"""
OAuth endpoints for handling third-party authentication.
"""

from typing import Any, Type

from fastapi import APIRouter, HTTPException, Request, status

from core.config import OAuthBaseSettings, OAuthGoogleSettings
from services.oauth_providers.base import BaseProvider
from services.oauth_providers.google import GoogleProvider

router = APIRouter()


class OAuthProviders:
    """A registry and factory for supported OAuth providers."""

    _providers: dict[str, tuple[Type[BaseProvider], Type[OAuthBaseSettings]]] = {
        "google": (GoogleProvider, OAuthGoogleSettings),
    }

    @classmethod
    def get_provider(cls, name: str) -> BaseProvider:
        """Retrieve an OAuth provider instance by name.

        Args:
            name: The name of the OAuth provider (e.g., "google").

        Returns:
            An instance of a subclass of BaseProvider.

        Raises:
            ValueError: If the given provider name is not supported.
        """
        provider_entry = cls._providers.get(name.lower())
        if not provider_entry:
            raise ValueError(f"Unsupported provider: {name}")

        provider_cls, settings_cls = provider_entry
        settings = settings_cls()
        return provider_cls(settings)


@router.get(
    "/login",
)
async def oauth_login(
    provider_name: str,
    request: Request,
) -> Any:
    """Initiate the OAuth login process for the given provider.

    Args:
        provider_name: The name of the OAuth provider (e.g., "google").
        request: The current HTTP request object.

    Returns:
        A URL string to redirect the user to the provider's authentication page.

    Raises:
        HTTPException: If the provider is not found or not supported.
    """
    provider = OAuthProviders.get_provider(provider_name)
    if provider:
        return await provider.get_auth_url(request)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{provider=} not found",
    )
