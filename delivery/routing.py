# ---------------------------------------------------------------------------
# Rutare reala pe strazi prin OSRM (Open Source Routing Machine).
# Foloseste serverul public demo. Returneaza distanta reala pe sosea, durata
# estimata si geometria traseului (lista de puncte [lat, lng]) pentru desenare.
#
# INLOCUIESTE IN PRODUCTIE: serverul public OSRM nu are garantii de uptime si
# are limite de utilizare. Pentru productie, gazduieste propriul OSRM sau
# foloseste Mapbox/Google Directions (cu cheie API).
# ---------------------------------------------------------------------------
import json
import urllib.request

from .data import road_distance_km

OSRM_BASE = "https://router.project-osrm.org"

# Cache simplu in memorie: aceeasi ruta nu se cere de doua ori de la OSRM.
_cache = {}


def _key(a, b):
    return (round(a["lng"], 5), round(a["lat"], 5), round(b["lng"], 5), round(b["lat"], 5))


def _fallback(a, b):
    """Daca OSRM nu raspunde, folosim o linie dreapta ca sa nu pice aplicatia."""
    return {
        "distanceKm": road_distance_km(a, b),
        "durationMin": None,
        "geometry": [[a["lat"], a["lng"]], [b["lat"], b["lng"]]],
        "source": "fallback",
    }


def get_route(a, b, timeout=5):
    """Ruta pe strazi intre doua puncte {lat, lng}. Rezultat cu cache."""
    key = _key(a, b)
    if key in _cache:
        return _cache[key]

    url = (
        f"{OSRM_BASE}/route/v1/driving/"
        f"{a['lng']},{a['lat']};{b['lng']},{b['lat']}"
        "?overview=full&geometries=geojson"
    )
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        route = payload["routes"][0]
        # OSRM da coordonate [lng, lat]; le intoarcem ca [lat, lng] pentru Leaflet.
        geometry = [[c[1], c[0]] for c in route["geometry"]["coordinates"]]
        result = {
            "distanceKm": round(route["distance"] / 1000, 1),
            "durationMin": max(1, round(route["duration"] / 60)),
            "geometry": geometry,
            "source": "osrm",
        }
    except Exception as exc:  # retea indisponibila, timeout, raspuns neasteptat etc.
        print("[rutare] OSRM indisponibil, folosesc linie dreapta:", exc)
        result = _fallback(a, b)

    _cache[key] = result
    return result


def get_route_multi(points, timeout=6):
    """Ruta pe strazi printr-o lista ordonata de puncte {lat, lng} (ridicare,
    0..N opriri intermediare, livrare). Returneaza distanta totala, durata si
    geometria combinata (lista [lat, lng]) de desenat pe harta."""
    pts = [p for p in points if p]
    if len(pts) < 2:
        return {"distanceKm": 0, "durationMin": None, "geometry": [], "source": "none"}
    if len(pts) == 2:  # cazul obisnuit: reutilizam ruta simpla (cu cache)
        return get_route(pts[0], pts[1], timeout)

    coords = ";".join(f"{p['lng']},{p['lat']}" for p in pts)
    url = f"{OSRM_BASE}/route/v1/driving/{coords}?overview=full&geometries=geojson"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        route = payload["routes"][0]
        geometry = [[c[1], c[0]] for c in route["geometry"]["coordinates"]]
        return {
            "distanceKm": round(route["distance"] / 1000, 1),
            "durationMin": max(1, round(route["duration"] / 60)),
            "geometry": geometry,
            "source": "osrm",
        }
    except Exception as exc:
        print("[rutare] OSRM multi indisponibil, concatenez linii drepte:", exc)
        dist = 0.0
        geom = []
        for a, b in zip(pts, pts[1:]):
            leg = _fallback(a, b)
            dist += leg["distanceKm"]
            if not geom:
                geom.append(leg["geometry"][0])
            geom.extend(leg["geometry"][1:])
        return {"distanceKm": round(dist, 1), "durationMin": None, "geometry": geom, "source": "fallback"}
