"""
ASGI config for geoapi project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from django.urls import path
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

django_asgi_app = get_asgi_application()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geoapi.settings")

from authentication.middleware import JWTAuthMiddleware  # noqa E402
from data.websocket.consumers import WorkerResponseConsumer  # noqa E402


routes = [
    path(
        "ws/geodata",
        WorkerResponseConsumer.as_asgi(),  # type: ignore
        name="worker_response",
    ),
]

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(URLRouter(routes)),
    }
)
