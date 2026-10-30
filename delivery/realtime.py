# ---------------------------------------------------------------------------
# Strat de timp real pentru urmarirea comenzilor.
#
# Cum functioneaza (fara Redis, un singur proces):
#  - Firul de simulare (delivery/simulation.py) muta soferul si avanseaza
#    starile in baza de date, la fel ca pana acum.
#  - Aici rulam, in bucla de evenimente ASGI (acelasi loop ca al consumerilor),
#    un "ceas" care, la ~1.2s, citeste din DB fiecare comanda urmarita activ si
#    o trimite (push) catre grupul ei de WebSocket. Asa evitam complet
#    problemele InMemoryChannelLayer intre thread-uri/loop-uri diferite.
#
# INLOCUIESTE IN PRODUCTIE: pentru mai multe procese/servere, foloseste un
# channel layer cu Redis (channels_redis) si fa broadcast direct din codul care
# schimba starea, in loc de acest ceas care citeste periodic DB.
# ---------------------------------------------------------------------------
import asyncio

from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

# Comenzi urmarite activ: cod -> numar de conexiuni WebSocket deschise.
_active = {}
# Numarul de soferi conectati la feed-ul de comenzi disponibile.
_drivers = 0
# Ultimul set de coduri disponibile trimis soferilor (pentru a detecta schimbari).
_last_available = None
_started = False

DRIVERS_GROUP = "drivers"


def group_name(code):
    return f"order_{code}"


def drivers_add():
    global _drivers
    _drivers += 1


def drivers_remove():
    global _drivers
    _drivers = max(0, _drivers - 1)


def active_add(code):
    _active[code] = _active.get(code, 0) + 1


def active_remove(code):
    if code in _active:
        _active[code] -= 1
        if _active[code] <= 0:
            del _active[code]


@database_sync_to_async
def _serialize(code):
    from .models import Order
    try:
        return Order.objects.get(code=code).serialize()
    except Order.DoesNotExist:
        return None


@database_sync_to_async
def _available_jobs():
    """Comenzile disponibile (fara sofer, in cautare) - vizibile oricarui sofer."""
    from .models import Order
    qs = Order.objects.filter(driver_user__isnull=True, status="cautare_sofer")
    return [o.serialize() for o in qs]


async def _broadcast_driver_feed(layer, force=False):
    """Trimite lista de comenzi disponibile soferilor, doar cand se schimba."""
    global _last_available
    jobs = await _available_jobs()
    codes = tuple(j["id"] for j in jobs)
    if force or codes != _last_available:
        _last_available = codes
        await layer.group_send(DRIVERS_GROUP, {"type": "driver.feed", "data": {"available": jobs}})


async def _loop():
    layer = get_channel_layer()
    while True:
        await asyncio.sleep(1.2)
        for code in list(_active.keys()):
            data = await _serialize(code)
            if data is None:
                continue
            await layer.group_send(group_name(code), {"type": "order.update", "data": data})
        if _drivers > 0:
            await _broadcast_driver_feed(layer)


def ensure_started():
    """Porneste ceasul o singura data, in loop-ul curent (al serverului ASGI)."""
    global _started
    if _started:
        return
    _started = True
    asyncio.create_task(_loop())
