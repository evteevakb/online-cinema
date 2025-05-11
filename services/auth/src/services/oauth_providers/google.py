"""
Google OAuth 2.0 provider implementation.
"""

from typing import Any

from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request

from core.config import OAuthGoogleSettings
from services.oauth_providers.base import BaseProvider


class GoogleProvider(BaseProvider):
    """OAuth 2.0 provider for Google."""

    provider_name = "google"

    def __init__(
        self,
        settings: OAuthGoogleSettings,
    ) -> None:
        """Initializes the Google provider with OAuth client configuration.

        Args:
            settings: An instance of OAuthGoogleSettings containing
                the client ID, client secret, auth/redirect URIs, and token URL.
        """
        self.oauth = OAuth()
        self.oauth.register(
            name=self.provider_name,
            client_id=settings.client_id,
            client_secret=settings.client_secret,
            authorize_url=settings.auth_uri,
            access_token_url=settings.token_uri,
            client_kwargs={"scope": "openid profile email"},
            server_metadata_url=settings.server_metadata_url,
        )
        self.redirect_uri = settings.redirect_uri

    async def get_auth_url(
        self,
        request: Request,
    ) -> Any:
        """Generate the Google OAuth authorization URL and redirect the user.

        Args:
            request: The current FastAPI Request object.

        Returns:
            A redirection response to Google's OAuth authorization URL.
        """
        return await self.oauth.google.authorize_redirect(request, self.redirect_uri)

    async def get_user_info(
        self,
        request: Request,
    ):
        try:
            data = await self.oauth.google.authorize_access_token(request)
            user_info = data["userinfo"]
            return user_info
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")
