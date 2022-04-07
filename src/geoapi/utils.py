from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpResponse, HttpRequest

from urllib.parse import urlparse


@database_sync_to_async
def get_user(token):
    authenticator = JWTAuthentication()
    payload = authenticator.get_validated_token(token)
    return payload["user"]


class JWTAuthMiddleware:
    """
    Custom middleware to process JWT tokens from query strings
    for ASGI requests.
    """

    def __init__(self, app: object):
        self.app = app

    def __call__(self, scope, receive, send):
        params = urlparse.parse_qs(scope["query_string"])
        scope["user"] = get_user(params.get("token"))


def healthcheck(request: HttpRequest) -> HttpResponse:
    """
    Simple heathcheck endpoint.
    """
    return HttpResponse("ok", status=200)
