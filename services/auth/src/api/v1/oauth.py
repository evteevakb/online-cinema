"""
OAuth endpoints for handling third-party authentication.
"""

from typing import Any, Type

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status

from core.config import OAuthBaseSettings, OAuthGoogleSettings, OAuthYandexSettings
from schemas.auth import TokenResponse
from services.auth import AuthService, get_auth_service
from services.oauth import get_oauth_service, OAuthService, Provider
from services.oauth_providers.base import BaseProvider
from services.oauth_providers.google import GoogleProvider
from services.oauth_providers.yandex import YandexProvider

router = APIRouter()
_providers: dict[str, tuple[Type[BaseProvider], Type[OAuthBaseSettings]]] = {
    Provider.GOOGLE: (GoogleProvider, OAuthGoogleSettings),
    Provider.YANDEX: (YandexProvider, OAuthYandexSettings),
}


def get_oauth_provider(
    provider_name: Provider = Path(..., alias="provider_name"),
) -> BaseProvider:
    """Retrieve an OAuth provider instance by name.

    Args:
        provider_name: The name of the OAuth provider (e.g., "google").

    Returns:
        An instance of a subclass of BaseProvider.

    Raises:
        HTTPException: If the specified provider is not supported.
    """
    provider_entry = _providers.get(provider_name.lower())
    if not provider_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider with {provider_name=} not found",
        )

    provider_cls, settings_cls = provider_entry
    settings = settings_cls()
    return provider_cls(settings)


@router.get(
    "/login/{provider_name}",
)
async def oauth_login(
    request: Request,
    provider: BaseProvider = Depends(get_oauth_provider),
) -> Any:
    """Initiate the OAuth login process for the specified provider.

    Args:
        request: The incoming HTTP request.
        provider: The OAuth provider instance.

    Returns:
        Any: A redirect response for the user to authenticate with the OAuth provider.
    """
    return await provider.get_redirect_url(request)


@router.get("/callback/{provider_name}")
async def callback(
    request: Request,
    provider: BaseProvider = Depends(get_oauth_provider),
    auth_service: AuthService = Depends(get_auth_service),
    oauth_service: OAuthService = Depends(get_oauth_service),
) -> TokenResponse:
    """Handle the OAuth callback and exchange the authorization code for user data
        and application-specific tokens.

    Args:
        request: The incoming HTTP request containing the OAuth callback parameters.
        provider: The OAuth provider instance.
        auth_service: The authentication service for issuing application-specific tokens.
        oauth_service: The service used to manage users with social accounts.

    Returns:
        TokenResponse: Contains access and refresh tokens for the authenticated user.
    """
    return await provider.authorize(
        request=request,
        auth_service=auth_service,
        oauth_service=oauth_service,
    )
