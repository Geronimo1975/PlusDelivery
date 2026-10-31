import datetime
import json
import random

from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from . import data
from . import matching
from .models import Order, Profile
from .routing import get_route, get_route_multi
from .geocoding import geocode as geocode_search


def _body(request):
    try:
        return json.loads(request.body or "{}")
    except (ValueError, TypeError):
        return {}


def _resolve_point(body, prefix):
    """Determina un punct {id, name, lat, lng} fie dintr-o locatie presetata
    (`<prefix>Id`), fie dintr-o adresa geocodata libera (`<prefix>` = obiect
    cu name/lat/lng, ex. din cautarea Nominatim din frontend)."""
    preset = data.find_location(body.get(prefix + "Id"))
    if preset:
        return dict(preset)
    custom = body.get(prefix)
    if isinstance(custom, dict) and custom.get("lat") is not None and custom.get("lng") is not None:
        try:
            return {
                "id": "custom",
                "name": custom.get("name", "Adresa aleasa"),
                "lat": float(custom["lat"]),
                "lng": float(custom["lng"]),
            }
        except (ValueError, TypeError):
            return None
    return None


def _resolve_stops(body):
    """Lista de opriri intermediare din body['stops'] (fiecare intrare: un reper
    presetat `{id}` sau o adresa libera `{name, lat, lng}`). Sare peste intrarile
    incomplete, pastrand ordinea aleasa de client."""
    out = []
    for raw in (body.get("stops") or []):
        if not isinstance(raw, dict):
            continue
        preset = data.find_location(raw.get("id"))
        if preset:
            out.append(dict(preset))
            continue
        if raw.get("lat") is not None and raw.get("lng") is not None:
            try:
                out.append({
                    "id": "custom",
                    "name": raw.get("name", "Oprire"),
                    "lat": float(raw["lat"]),
                    "lng": float(raw["lng"]),
                })
            except (ValueError, TypeError):
                continue
    return out


def _validate_route_points(points):
    """Verifica un traseu ordonat de puncte: toate in zona, fara doua puncte
    consecutive identice. Returneaza un mesaj de eroare sau None daca e valid."""
    for p in points:
        if not data.within_service_area(p):
            return (f"Momentan livram doar in raza de {data.MAX_RADIUS_KM} km "
                    f"fata de {data.SERVICE_CENTER['name']}.")
    for a, b in zip(points, points[1:]):
        if a["lat"] == b["lat"] and a["lng"] == b["lng"]:
            return "Punctele consecutive de pe traseu trebuie sa fie diferite."
    return None


def _resolve_schedule(body):
    """Interpreteaza body['scheduledFor'] (timestamp ms sau sir ISO). Returneaza
    (datetime_aware | None, mesaj_eroare | None). None, None = comanda instant.
    Regula: cel putin 5 minute in viitor, cel mult 30 de zile."""
    raw = body.get("scheduledFor")
    if raw in (None, "", 0):
        return None, None
    try:
        if isinstance(raw, (int, float)):
            dt = datetime.datetime.fromtimestamp(raw / 1000, tz=datetime.timezone.utc)
        else:
            dt = datetime.datetime.fromisoformat(str(raw))
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
    except (ValueError, TypeError, OverflowError, OSError):
        return None, "Data programarii nu este valida."
    now = timezone.now()
    if dt < now + datetime.timedelta(minutes=5):
        return None, "Alege o ora cel putin 5 minute in viitor."
    if dt > now + datetime.timedelta(days=30):
        return None, "Poti programa cel mult cu 30 de zile inainte."
    return dt, None


def _require(request, role=None):
    """(user, None) daca e autentificat (si are rolul cerut); altfel
    (None, raspuns de eroare 401/403)."""
    if not request.user.is_authenticated:
        return None, JsonResponse({"error": "Trebuie sa fii autentificat."}, status=401)
    if role and getattr(request.user.profile, "role", None) != role:
        return None, JsonResponse({"error": "Nu ai acces la aceasta sectiune."}, status=403)
    return request.user, None


# --- Pagina principala -----------------------------------------------------
@ensure_csrf_cookie  # seteaza cookie-ul CSRF la incarcarea paginii (pt. POST-uri)
def index(request):
    return render(request, "index.html")


# --- Date de referinta pentru interfata ------------------------------------
def config(request):
    from .models import VehicleClass, Capability, Vertical
    return JsonResponse({
        "serviceTypes": data.SERVICE_TYPES,
        "vehicles": data.VEHICLES,
        "locations": data.LOCATIONS,
        "flow": data.ORDER_FLOW,
        "serviceCenter": data.SERVICE_CENTER,
        "maxRadiusKm": data.MAX_RADIUS_KM,
        # Taxonomia (pentru formularele de domeniu si de vehicul)
        "vehicleClasses": [
            {"slug": c.slug, "name": c.name, "rank": c.rank, "maxWeightKg": c.max_weight_kg}
            for c in VehicleClass.objects.filter(active=True)],
        "capabilities": [
            {"slug": c.slug, "name": c.name, "needsDocument": c.needs_document}
            for c in Capability.objects.all()],
        "verticals": [
            {"slug": v.slug, "name": v.name, "orderFields": v.order_fields or []}
            for v in Vertical.objects.filter(active=True)],
    })


# --- Taxonomia pe verticale (domenii + cerinte vehicul) --------------------
def verticals(request):
    """Lista verticalelor active + cerintele lor (clasa minima, capabilitati,
    licente, campuri specifice). Date de referinta pentru interfata."""
    from .models import Vertical
    out = []
    for v in Vertical.objects.filter(active=True).select_related("min_vehicle_class"):
        out.append({
            "slug": v.slug,
            "name": v.name,
            "description": v.description,
            "minClass": v.min_vehicle_class.slug if v.min_vehicle_class_id else None,
            "capabilities": list(v.required_capabilities.values_list("slug", flat=True)),
            "licenses": v.required_licenses or [],
            "orderFields": v.order_fields or [],
        })
    return JsonResponse({"verticals": out})


# --- Geocodare adresa libera (Nominatim) -----------------------------------
def geocode(request):
    q = request.GET.get("q", "")
    return JsonResponse({"results": geocode_search(q)})


# --- Oferta de pret --------------------------------------------------------
def quote(request):
    b = _body(request)
    frm = _resolve_point(b, "from")
    to = _resolve_point(b, "to")
    if not frm or not to:
        return JsonResponse({"error": "Alege punctul de ridicare si de livrare."}, status=400)
    stops = _resolve_stops(b)
    points = [frm] + stops + [to]  # traseul complet, in ordine
    err = _validate_route_points(points)
    if err:
        return JsonResponse({"error": err}, status=400)

    route = get_route_multi(points)  # distanta reala pe strazi (OSRM), prin opriri
    km = route["distanceKm"]
    service_type = b.get("serviceType")
    vehicles = [v for v in data.VEHICLES if not service_type or v["service"] == service_type]
    quotes = []
    for v in vehicles:
        q = data.quote_for_vehicle(v, km)
        q.update({"name": v["name"], "capacity": v["capacity"], "service": v["service"]})
        quotes.append(q)
    return JsonResponse({"distanceKm": km, "routeSource": route["source"], "quotes": quotes})


# --- Listare + creare comenzi (acelasi URL, metode diferite) ---------------
def orders(request):
    if request.method == "POST":
        return _create_order(request)
    # GET: comenzile proprii (clientul le creeaza, soferul le livreaza)
    user, err = _require(request)
    if err:
        return err
    qs = Order.objects.filter(client=user) if user.profile.role == "client" \
        else Order.objects.filter(driver_user=user)
    return JsonResponse([o.serialize() for o in qs], safe=False)


def _create_order(request):
    user, err = _require(request, "client")
    if err:
        return err
    b = _body(request)
    frm = _resolve_point(b, "from")
    to = _resolve_point(b, "to")
    vehicle = data.find_vehicle(b.get("vehicleId"))
    if not frm or not to or not vehicle:
        return JsonResponse({"error": "Date incomplete pentru comanda."}, status=400)
    stops = _resolve_stops(b)
    points = [frm] + stops + [to]
    err = _validate_route_points(points)
    if err:
        return JsonResponse({"error": err}, status=400)

    scheduled_for, err = _resolve_schedule(b)
    if err:
        return JsonResponse({"error": err}, status=400)

    from .models import Vertical
    vertical = None
    vertical_fields = {}
    vslug = b.get("verticalSlug")
    if vslug:
        vertical = Vertical.objects.filter(slug=vslug, active=True).first()
        if not vertical:
            return JsonResponse({"error": "Domeniu invalid."}, status=400)
        vertical_fields, err = _resolve_vertical_fields(vertical, b.get("verticalFields") or {})
        if err:
            return JsonResponse({"error": err}, status=400)

    route = get_route_multi(points)
    q = data.quote_for_vehicle(vehicle, route["distanceKm"])
    order = Order.objects.create(
        client=user,
        service_type=b.get("serviceType") or vehicle["service"],
        vehicle_id=vehicle["id"], vehicle_name=vehicle["name"],
        from_id=frm["id"], from_name=frm["name"], from_lat=frm["lat"], from_lng=frm["lng"],
        to_id=to["id"], to_name=to["name"], to_lat=to["lat"], to_lng=to["lng"],
        stops=[{"name": s["name"], "lat": s["lat"], "lng": s["lng"]} for s in stops],
        note=b.get("note", ""), contact=b.get("contact") or user.profile.phone,
        price=q["price"], distance_km=q["distanceKm"], eta_min=q["etaMin"],
        route_geometry=route["geometry"],
        scheduled_for=scheduled_for,
        status=data.SCHEDULED_STATUS if scheduled_for else data.ORDER_FLOW[0]["id"],
        vertical=vertical,
        vertical_fields=vertical_fields,
    )
    return JsonResponse(order.serialize(), status=201)


def _resolve_vertical_fields(vertical, raw):
    """Valideaza valorile campurilor specifice domeniului fata de definitia
    din `vertical.order_fields`. Pastreaza doar cheile definite; cere valoare
    pentru cele `required`. Returneaza (dict_curat, mesaj_eroare|None)."""
    if not isinstance(raw, dict):
        raw = {}
    out = {}
    for f in (vertical.order_fields or []):
        key = f.get("key")
        if not key:
            continue
        val = raw.get(key)
        if f.get("type") == "bool":
            val = bool(val)
        elif val is not None:
            val = str(val).strip()
        if f.get("required") and (val in (None, "", False)):
            return None, f"Campul „{f.get('label', key)}” este obligatoriu pentru {vertical.name}."
        if val not in (None, ""):
            out[key] = val
    return out, None


# --- O comanda (urmarire) --------------------------------------------------
def order_detail(request, code):
    user, err = _require(request)
    if err:
        return err
    try:
        order = Order.objects.get(code=code)
    except Order.DoesNotExist:
        return JsonResponse({"error": "Comanda inexistenta."}, status=404)
    # doar clientul proprietar sau soferul atribuit pot vedea comanda
    if order.client_id != user.id and order.driver_user_id != user.id and not user.is_staff:
        return JsonResponse({"error": "Nu ai acces la aceasta comanda."}, status=403)
    return JsonResponse(order.serialize())


# --- Panou sofer: comenzi disponibile + ale mele + castig estimat ----------
def driver_jobs(request):
    user, err = _require(request, "driver")
    if err:
        return err
    # Doar comenzile pe care vehiculul curierului le poate duce (clasa + capabilitati).
    rank, caps = matching.driver_profile(user)
    available_all = Order.objects.filter(driver_user__isnull=True, status="cautare_sofer")
    available = [o for o in available_all if matching.eligible(o._requires(), rank, caps)]
    mine_active = Order.objects.filter(driver_user=user).exclude(status="livrat")
    done = list(Order.objects.filter(driver_user=user, status="livrat"))

    # Castig pe ultimele 7 zile. Folosim data crearii ca proxy pentru ziua livrarii
    # (prototipul nu stocheaza momentul exact al livrarii).
    # INLOCUIESTE IN PRODUCTIE: un camp delivered_at setat la trecerea in "livrat".
    ro_days = ["Lu", "Ma", "Mi", "Jo", "Vi", "Sâ", "Du"]  # weekday(): Luni=0
    today = timezone.localtime().date()
    week = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
    totals = {d: 0.0 for d in week}
    counts = {d: 0 for d in week}
    for o in done:
        d = timezone.localtime(o.created_at).date()
        if d in totals:
            totals[d] += o.price
            counts[d] += 1
    earnings_by_day = [{
        "label": ro_days[d.weekday()],
        "date": d.isoformat(),
        "total": round(totals[d], 2),
        "count": counts[d],
    } for d in week]

    return JsonResponse({
        "available": [o.serialize() for o in available],
        "mine": [o.serialize() for o in mine_active],
        "earnings": round(sum(o.price for o in done), 2),
        "deliveredCount": len(done),
        "earningsByDay": earnings_by_day,
        "online": user.profile.online,
        "vehicleProfile": {"rank": rank, "caps": sorted(caps)},
    })


# --- Sofer: comuta online/offline ------------------------------------------
def driver_online(request, *args):
    user, err = _require(request, "driver")
    if err:
        return err
    b = _body(request)
    user.profile.online = bool(b.get("online"))
    user.profile.save(update_fields=["online"])
    return JsonResponse({"online": user.profile.online})


# --- Sofer: profilul de vehicul (clasa + capabilitati, cu asumarea raspunderii)
def driver_vehicle(request):
    user, err = _require(request, "driver")
    if err:
        return err
    from .models import VehicleClass, Capability, TransporterVehicle

    def serialize(v):
        if not v:
            return None
        return {
            "classSlug": v.vehicle_class.slug,
            "className": v.vehicle_class.name,
            "capabilities": list(v.capabilities.values_list("slug", flat=True)),
            "label": v.label, "plate": v.plate,
            "responsibilityAccepted": v.responsibility_accepted,
            "verified": v.verified,
        }

    current = (TransporterVehicle.objects.filter(owner=user, active=True)
               .select_related("vehicle_class").order_by("-id").first())

    if request.method != "POST":
        return JsonResponse({"vehicle": serialize(current)})

    b = _body(request)
    cls = VehicleClass.objects.filter(slug=b.get("classSlug"), active=True).first()
    if not cls:
        return JsonResponse({"error": "Alege o clasa de vehicul valida."}, status=400)
    if not b.get("responsibilityAccepted"):
        return JsonResponse({"error": "Trebuie sa iti asumi raspunderea pentru transport."}, status=400)
    caps = list(Capability.objects.filter(slug__in=(b.get("capabilities") or [])))

    veh = current or TransporterVehicle(owner=user)
    veh.vehicle_class = cls
    veh.label = b.get("label", "") or veh.label
    veh.plate = b.get("plate", "") or veh.plate
    veh.responsibility_accepted = True
    veh.active = True
    # INLOCUIESTE IN PRODUCTIE: verificarea reala a documentelor se face de admin.
    # In prototip aprobam automat ca matching-ul sa functioneze end-to-end.
    veh.verified = True
    veh.save()
    veh.capabilities.set(caps)
    return JsonResponse({"vehicle": serialize(veh)})


# --- Sofer accepta ---------------------------------------------------------
def accept_order(request, code):
    user, err = _require(request, "driver")
    if err:
        return err
    try:
        order = Order.objects.get(code=code)
    except Order.DoesNotExist:
        return JsonResponse({"error": "Comanda inexistenta."}, status=404)
    if order.driver_user_id:
        return JsonResponse({"error": "Comanda are deja sofer."}, status=409)

    p = user.profile
    order.driver_user = user
    order.driver_id = f"u{user.id}"
    order.driver_name = p.display_name()
    order.driver_rating = p.rating
    # soferul porneste putin departe de punctul de ridicare
    order.driver_lat = order.from_lat + 0.01
    order.driver_lng = order.from_lng - 0.01
    order.status = "acceptat"
    order.save()
    return JsonResponse(order.serialize())


# --- Avansare manuala a starii (doar soferul atribuit) ---------------------
def advance_status(request, code):
    user, err = _require(request, "driver")
    if err:
        return err
    try:
        order = Order.objects.get(code=code)
    except Order.DoesNotExist:
        return JsonResponse({"error": "Comanda inexistenta."}, status=404)
    if order.driver_user_id != user.id:
        return JsonResponse({"error": "Aceasta comanda nu este atribuita tie."}, status=403)
    flow_ids = [f["id"] for f in data.ORDER_FLOW]
    idx = flow_ids.index(order.status)
    if idx < len(flow_ids) - 1:
        order.status = flow_ids[idx + 1]
        order.save()
    return JsonResponse(order.serialize())


# --- Client evalueaza soferul dupa livrare ---------------------------------
def rate_order(request, code):
    user, err = _require(request, "client")
    if err:
        return err
    try:
        order = Order.objects.get(code=code)
    except Order.DoesNotExist:
        return JsonResponse({"error": "Comanda inexistenta."}, status=404)
    if order.client_id != user.id:
        return JsonResponse({"error": "Nu este comanda ta."}, status=403)
    if order.status != "livrat":
        return JsonResponse({"error": "Poti evalua doar dupa livrare."}, status=400)
    if order.rating is not None:
        return JsonResponse({"error": "Comanda a fost deja evaluata."}, status=409)

    try:
        rating = int(_body(request).get("rating"))
    except (TypeError, ValueError):
        rating = 0
    if rating < 1 or rating > 5:
        return JsonResponse({"error": "Nota trebuie sa fie intre 1 si 5."}, status=400)

    order.rating = rating
    order.save(update_fields=["rating"])

    # recalculam media soferului din toate comenzile lui evaluate
    if order.driver_user_id:
        rated = Order.objects.filter(driver_user_id=order.driver_user_id, rating__isnull=False)
        avg = sum(o.rating for o in rated) / rated.count()
        p = order.driver_user.profile
        p.rating = round(avg, 2)
        p.save(update_fields=["rating"])

    return JsonResponse(order.serialize())


# --- Statistici business (pe comenzile clientului autentificat) ------------
def stats(request):
    user, err = _require(request, "client")
    if err:
        return err
    qs = Order.objects.filter(client=user)
    total = qs.count()
    livrate = qs.filter(status="livrat").count()
    venit = round(sum(o.price for o in qs), 2)
    return JsonResponse({
        "total": total,
        "livrate": livrate,
        "active": total - livrate,
        "venit": venit,
        "soferiOnline": Profile.objects.filter(role="driver", online=True).count(),
    })
