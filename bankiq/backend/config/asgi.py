"""ASGI config — HTTP via Django + WebSocket via Channels."""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

django_asgi_app = get_asgi_application()

from apps.agent.routing import websocket_urlpatterns  # noqa: E402
from config.middleware import JwtQueryAuthMiddleware

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JwtQueryAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
