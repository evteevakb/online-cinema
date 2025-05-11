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
    "/login/{provider_name}",
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


@router.get("/callback/{provider_name}")
async def callback(
    provider_name: str,
    request: Request,
):
    provider = OAuthProviders.get_provider(provider_name)
    if provider:
        user_info = await provider.get_user_info(request)
        user_social_id = user_info["sub"]

        # TODO: check if social ID already exists

        #  'sub': '111699460460291326721', 'email': 'evteeva.kb@gmail.com', 'email_verified': True, 'at_hash': 'MWFzeLZwxfLyBis57nyWDQ', 'nonce': 'VhCgfHZLWyD95qO6g4TN', 'name': 'Ksenia Evteeva', 'picture': 'https://lh3.googleusercontent.com/a/ACg8ocLjuujvsZtqgyvMOhmd6VPAG8zsqaMpEM3f-NGuW7k97CRCIf0=s96-c', 'given_name': 'Ksenia', 'family_name': 'Evteeva', 'iat': 1746896433, 'exp': 1746900033}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{provider=} not found",
    )
