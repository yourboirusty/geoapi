"""
ASGI config for geoapi project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from authentication.middleware import JWTAuthMiddleware
from data.websocket.consumers import WorkerResponseConsumer

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

routes = [
    path(
        "ws/geodata/<task_id>",
        WorkerResponseConsumer.as_asgi(),  # type: ignore
        name="worker_response",
    ),
]

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JWTAuthMiddleware(URLRouter(routes)),
    }
)
