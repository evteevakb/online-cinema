from fastapi import APIRouter, Request, Depends
from starlette.responses import RedirectResponse

from oauth.yandex import get_oauth_yandex_provider

router = APIRouter()

@router.get("/login")
async def login(request: Request, provider = Depends(get_oauth_yandex_provider)) -> RedirectResponse:
    redirect_uri = 'http://localhost:82/api/v1/oauth/yandex/authorize'
    return await provider.get_redirect_url(request, redirect_uri)


@router.get("/authorize")
async def authorize(request: Request, provider = Depends(get_oauth_yandex_provider)):
    token = await provider.authorize(request)
    return token
