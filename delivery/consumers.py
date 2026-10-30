# ---------------------------------------------------------------------------
# Consumer WebSocket pentru urmarirea live a unei comenzi.
# Clientul (proprietarul) sau soferul atribuit se conecteaza la
# ws/track/<cod>/ si primeste starea comenzii la fiecare actualizare (push),
# fara polling din browser.
# ---------------------------------------------------------------------------
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from . import realtime


class OrderTrackConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.code = self.scope["url_route"]["kwargs"]["code"]
        user = self.scope.get("user")
        if user is None or not user.is_authenticated:
            await self.close(code=4401)  # neautentificat
            return

        data = await self._load(self.code, user.id, user.is_staff)
        if data is None:
            await self.close(code=4403)  # inexistenta sau fara acces
            return

        self.group = realtime.group_name(self.code)
        await self.channel_layer.group_add(self.group, self.channel_name)
        realtime.active_add(self.code)
        realtime.ensure_started()
        await self.accept()
        await self.send(text_data=json.dumps(data))  # starea curenta imediat

    async def disconnect(self, code):
        if hasattr(self, "group"):
            await self.channel_layer.group_discard(self.group, self.channel_name)
            realtime.active_remove(self.code)

    async def receive(self, text_data=None, bytes_data=None):
        pass  # clientul doar asculta

    # mesaj trimis catre grup cu type "order.update"
    async def order_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    @database_sync_to_async
    def _load(self, code, uid, is_staff):
        from .models import Order
        try:
            o = Order.objects.get(code=code)
        except Order.DoesNotExist:
            return None
        if o.client_id != uid and o.driver_user_id != uid and not is_staff:
            return None
        return o.serialize()


class DriverFeedConsumer(AsyncWebsocketConsumer):
    """Feed live de comenzi disponibile pentru soferi (notificare comanda noua)."""

    async def connect(self):
        user = self.scope.get("user")
        if user is None or not user.is_authenticated:
            await self.close(code=4401)
            return
        if not await self._is_driver(user.id):
            await self.close(code=4403)
            return
        await self.channel_layer.group_add(realtime.DRIVERS_GROUP, self.channel_name)
        realtime.drivers_add()
        realtime.ensure_started()
        await self.accept()
        # trimite imediat lista curenta de comenzi disponibile
        jobs = await realtime._available_jobs()
        await self.send(text_data=json.dumps({"available": jobs}))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(realtime.DRIVERS_GROUP, self.channel_name)
        realtime.drivers_remove()

    async def receive(self, text_data=None, bytes_data=None):
        pass

    async def driver_feed(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    @database_sync_to_async
    def _is_driver(self, uid):
        from .models import Profile
        return Profile.objects.filter(user_id=uid, role="driver").exists()
