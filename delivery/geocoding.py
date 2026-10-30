# ---------------------------------------------------------------------------
# Geocodare libera a adreselor prin Nominatim (OpenStreetMap), gratuit, fara
# cheie API. Transforma textul scris de utilizator ("Reeperbahn 1, Hamburg")
# in coordonate lat/lng, limitat la zona Hamburg + imprejurimi.
#
# INLOCUIESTE IN PRODUCTIE: serverul public Nominatim cere un User-Agent real
# si are o limita de ~1 cerere/secunda (politica de utilizare). Pentru productie
# gazduieste propriul Nominatim sau foloseste un serviciu platit
# (Mapbox / Google Geocoding) cu cheie API.
# ---------------------------------------------------------------------------
import json
import urllib.parse
import urllib.request

from .data import within_service_area

NOMINATIM_BASE = "https://nominatim.openstreetmap.org/search"
# Nominatim cere un User-Agent care sa identifice aplicatia (altfel da 403).
# INLOCUIESTE IN PRODUCTIE: pune aici numele si un contact real al aplicatiei.
USER_AGENT = "PlusDelivery/1.0 (prototip demo marketplace livrari)"

# Chenar aproximativ in jurul Hamburg (ca sa prioritizam rezultatele locale).
# left,top,right,bottom = lng_vest, lat_nord, lng_est, lat_sud
VIEWBOX = "8.6,54.5,11.4,52.9"

# Cache simplu in memorie: aceeasi cautare nu se cere de doua ori.
_cache = {}


def geocode(query, limit=6, timeout=5):
    """Cauta adrese dupa text. Intoarce o lista de
    {name, lat, lng, inArea} limitata la zona de serviciu afisabila."""
    q = (query or "").strip()
    if len(q) < 3:
        return []
    if q in _cache:
        return _cache[q]

    params = urllib.parse.urlencode({
        "q": q,
        "format": "jsonv2",
        "addressdetails": 0,
        "limit": limit,
        "countrycodes": "de",
        "viewbox": VIEWBOX,
        "bounded": 1,  # restrange rezultatele la chenarul Hamburg
        "accept-language": "de",
    })
    url = f"{NOMINATIM_BASE}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # retea indisponibila, timeout, raspuns neasteptat
        print("[geocodare] Nominatim indisponibil:", exc)
        return []

    results = []
    for item in payload:
        try:
            lat = float(item["lat"])
            lng = float(item["lon"])
        except (KeyError, ValueError, TypeError):
            continue
        point = {"lat": lat, "lng": lng}
        results.append({
            "name": item.get("display_name", q),
            "lat": lat,
            "lng": lng,
            "inArea": within_service_area(point),
        })

    _cache[q] = results
    return results
