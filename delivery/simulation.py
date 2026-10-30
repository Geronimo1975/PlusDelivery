# ---------------------------------------------------------------------------
# SIMULARE: un fir de executie (thread) care avanseaza comenzile la fiecare 2s,
# muta soferul pe traseu si schimba starile. Echivalentul vechiului setInterval.
# INLOCUIESTE IN PRODUCTIE: pozitii GPS reale de la aplicatia soferului + un
# sistem de task-uri (ex. Celery) in loc de acest thread din serverul de dezvoltare.
# ---------------------------------------------------------------------------
import threading
import time

_started = False


def _lerp(a, b, t):
    return {"lat": a["lat"] + (b["lat"] - a["lat"]) * t,
            "lng": a["lng"] + (b["lng"] - a["lng"]) * t}


def _near(a, b):
    return abs(a["lat"] - b["lat"]) < 0.003 and abs(a["lng"] - b["lng"]) < 0.003


def _point_along(geometry, t):
    """Pozitia pe traseul real (lista [lat, lng]) la fractiunea t din 0..1,
    masurata dupa lungimea cumulata a segmentelor."""
    if not geometry:
        return None
    if len(geometry) == 1 or t <= 0:
        return {"lat": geometry[0][0], "lng": geometry[0][1]}
    if t >= 1:
        return {"lat": geometry[-1][0], "lng": geometry[-1][1]}

    seg_len = []
    total = 0.0
    for i in range(len(geometry) - 1):
        a, b = geometry[i], geometry[i + 1]
        d = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
        seg_len.append(d)
        total += d
    if total == 0:
        return {"lat": geometry[0][0], "lng": geometry[0][1]}

    target = t * total
    acc = 0.0
    for i, d in enumerate(seg_len):
        if acc + d >= target:
            r = (target - acc) / d if d else 0
            a, b = geometry[i], geometry[i + 1]
            return {"lat": a[0] + (b[0] - a[0]) * r, "lng": a[1] + (b[1] - a[1]) * r}
        acc += d
    return {"lat": geometry[-1][0], "lng": geometry[-1][1]}


def advance(order):
    frm = {"lat": order.from_lat, "lng": order.from_lng}
    to = {"lat": order.to_lat, "lng": order.to_lng}
    pos = {"lat": order.driver_lat, "lng": order.driver_lng} if order.driver_lat is not None else frm

    if order.status == "acceptat":
        order.status = "spre_ridicare"
    elif order.status == "spre_ridicare":
        pos = _lerp(pos, frm, 0.34)
        if _near(pos, frm):
            pos = dict(frm)
            order.status = "ridicat"
        order.driver_lat, order.driver_lng = pos["lat"], pos["lng"]
    elif order.status == "ridicat":
        order.status = "in_livrare"
    elif order.status == "in_livrare":
        order.progress = min(1.0, order.progress + 0.2)
        # urmeaza traseul real pe strazi daca exista; altfel linie dreapta
        geom = order.route_geometry or [[frm["lat"], frm["lng"]], [to["lat"], to["lng"]]]
        pos = _point_along(geom, order.progress)
        order.driver_lat, order.driver_lng = pos["lat"], pos["lng"]
        if order.progress >= 1.0:
            order.status = "livrat"
    order.save()


def tick():
    from .models import Order
    qs = Order.objects.exclude(status="livrat").filter(driver_id__isnull=False)
    for order in qs:
        advance(order)


def _loop():
    while True:
        time.sleep(2)
        try:
            tick()
        except Exception as exc:  # nu lasam thread-ul sa moara la o eroare izolata
            print("[simulare] eroare:", exc)


def start_simulation():
    global _started
    if _started:
        return
    _started = True
    threading.Thread(target=_loop, daemon=True).start()
    print("[simulare] pornita (avanseaza comenzile la fiecare 2s)")
