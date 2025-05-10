from authlib.integrations.starlette_client import OAuth
from fastapi import Request, Depends

from oauth.provider_base import BaseProvider
from core.config import YandexProviderSettings

from schemas.auth import TokenResponse
from starlette.responses import RedirectResponse

from services.auth import AuthService, get_auth_service

yandex_settings = YandexProviderSettings()

oauth = OAuth()

oauth.register(
    name=yandex_settings.name,
    client_id=yandex_settings.client_id,
    client_secret=yandex_settings.client_secret,
    access_token_url=yandex_settings.access_token_url,
    authorize_url=yandex_settings.authorize_url,
    api_base_url=yandex_settings.api_base_url
)


class YandexProvider(BaseProvider):
    """OAuth 2.0 provider for Yandex."""
    def __init__(self, auth_service):
        self.auth_service = auth_service

    async def get_redirect_url(self, request: Request, redirect_uri: str) -> RedirectResponse:
        return await oauth.yandex.authorize_redirect(request, redirect_uri)

    async def callback(self, request: Request) -> dict:
        token = await oauth.yandex.authorize_access_token(request)
        user_info_response = await oauth.yandex.get('info', token=token)
        user_info = user_info_response.json()
        return user_info

    async def authorize(
            self,
            request: Request
    ) -> TokenResponse:
        user_info = await self.callback(request)
        social_id = user_info.get('id')
        email = user_info.get('default_email')
        user_agent = request.headers.get("user-agent", "unknown")

        # user = get_or_create_social_user(social_id, email)
        token = await self.auth_service.login('admin@admin.com', '1234', user_agent)
        return token


def get_oauth_yandex_provider(
        auth_service: AuthService = Depends(get_auth_service)
) -> AuthService:
    return YandexProvider(auth_service)
