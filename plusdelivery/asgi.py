"""
Configurare ASGI pentru PlusDelivery.
HTTP e servit de Django ca de obicei; WebSocket (urmarire live) e servit de
Django Channels. Sub `runserver`, Channels porneste automat serverul ASGI.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plusdelivery.settings")

# Initializam aplicatia Django (incarca appurile) INAINTE de a importa consumers.
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402

from delivery.ws_urls import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # AuthMiddlewareStack aduce sesiunea + user-ul in scope (cookie-uri WS).
    "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
})
