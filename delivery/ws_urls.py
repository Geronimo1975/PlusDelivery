from django.urls import re_path

from . import consumers

# Rute WebSocket:
#  - ws/track/<cod>/ : urmarirea live a unei comenzi (client / sofer atribuit)
#  - ws/driver/      : feed de comenzi disponibile (notificare comanda noua)
websocket_urlpatterns = [
    re_path(r"ws/track/(?P<code>[\w-]+)/$", consumers.OrderTrackConsumer.as_asgi()),
    re_path(r"ws/driver/$", consumers.DriverFeedConsumer.as_asgi()),
]
