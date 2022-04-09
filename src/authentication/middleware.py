from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
    InvalidToken,
)
import jwt
from django.conf import settings
from urllib.parse import urlparse, parse_qs


@database_sync_to_async
def get_user(token):
    authenticator = JWTAuthentication()
    authenticator.get_validated_token(token)
    claims = jwt.decode(token, options={"verify_signature": False})
    return claims


class JWTAuthMiddleware:
    """
    Custom middleware to process JWT tokens from query strings
    for ASGI requests.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_params = parse_qs(scope["query_string"].decode("utf-8"))
        try:
            user = await get_user(query_params["token"][0])
            scope["user"] = user
        except (InvalidToken, KeyError, IndexError):
            pass
        return await self.app(scope, receive, send)
