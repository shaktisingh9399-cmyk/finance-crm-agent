"""Custom middleware to authenticate Django Channels connections using SimpleJWT."""

from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

from agent_core.enums import JwtClaim, QueryParam, ScopeKey

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_string: str):
    try:
        token = AccessToken(token_string)
        user_id = token[JwtClaim.USER_ID.value]
        return User.objects.get(pk=user_id)
    except Exception:
        return AnonymousUser()


class JwtQueryAuthMiddleware:
    """ASGI middleware to authenticate Channels connections using JWT token in query string."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get(ScopeKey.QUERY_STRING.value, b"").decode("utf8")
        query_params = parse_qs(query_string)
        token = query_params.get(QueryParam.TOKEN.value, [None])[0]

        if token:
            scope[ScopeKey.USER.value] = await get_user_from_token(token)
        else:
            scope[ScopeKey.USER.value] = AnonymousUser()

        return await self.app(scope, receive, send)
