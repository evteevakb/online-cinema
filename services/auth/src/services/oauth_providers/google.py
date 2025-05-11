"""
Google OAuth 2.0 provider implementation.
"""

from typing import Any

from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request

from core.config import OAuthGoogleSettings
from schemas.auth import TokenResponse
from services.auth import AuthService
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

    async def get_redirect_url(
        self,
        request: Request,
    ) -> Any:
        """Generate the Google OAuth authorization URL and redirect the user.

        Args:
            request: The current FastAPI Request object.

        Returns:
            Any: A redirection response to Google's OAuth authorization URL.
        """
        return await self.oauth.google.authorize_redirect(request, self.redirect_uri)

    async def get_user_info(
        self,
        request: Request,
    ) -> Any:
        """Exchange the authorization code for an access token and retrieve user information.

        Args:
            request: The incoming FastAPI request containing the authorization code.

        Returns:
            Any: User information obtained from Google's userinfo endpoint.

        Raises:
            HTTPException: If token exchange or user info retrieval fails.
        """
        try:
            data = await self.oauth.google.authorize_access_token(request)
            return data["userinfo"]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")

    async def authorize(
        self,
        request: Request,
        auth_service: AuthService,
    ) -> TokenResponse:
        """Authorize the user in the application based on their Google account.

        Args:
            request: The incoming FastAPI request with the authorization code.
            auth_service: The application-level authentication service used to issue tokens.

        Returns:
            TokenResponse: The application's access and refresh tokens for the user.
        """
        user_info = await self.get_user_info(request)
        # TODO: move obtaining needed data to get_user_info and validate it with Pydantic model
        social_id = user_info.get("sub")
        email = user_info.get("email")
        user_agent = request.headers.get("user-agent", "unknown")
        # TODO: need to finish logic
        # user = get_or_create_social_user(social_id, email)
        token = await auth_service.login("admin@admin.com", "1234", user_agent)
        return token
