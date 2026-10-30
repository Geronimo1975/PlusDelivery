# ---------------------------------------------------------------------------
# PlusDelivery - date de referinta + logica de pret, distanta si zona de serviciu
# (portare a vechiului src/data.js in Python). Zona: Hamburg + 100 km.
# ---------------------------------------------------------------------------
from math import radians, sin, cos, asin, sqrt

# Tipuri de serviciu (categoria mare de livrare)
SERVICE_TYPES = [
    {"id": "paket", "name": "Colete & marfa",
     "description": "Documente, colete mici si medii, cumparaturi, mancare."},
    {"id": "fracht", "name": "Transport & fret",
     "description": "Mobila, electrocasnice, paleti, mutari, obiecte voluminoase."},
]

# Tipuri de vehicul. Pret = base + per_km * km + per_min * minute.
VEHICLES = [
    {"id": "bicicleta", "service": "paket", "name": "Bicicleta / curier", "capacity": "pana la 8 kg", "base": 3.5, "per_km": 0.9, "per_min": 0.12, "speed_kmh": 16},
    {"id": "scuter", "service": "paket", "name": "Scuter / motocicleta", "capacity": "pana la 20 kg", "base": 4.5, "per_km": 1.1, "per_min": 0.18, "speed_kmh": 24},
    {"id": "masina", "service": "paket", "name": "Masina (break)", "capacity": "pana la 200 kg", "base": 6.0, "per_km": 1.3, "per_min": 0.22, "speed_kmh": 28},
    {"id": "transporter", "service": "fracht", "name": "Transporter / duba", "capacity": "pana la 1.000 kg", "base": 15, "per_km": 1.8, "per_min": 0.35, "speed_kmh": 26},
    {"id": "camion35", "service": "fracht", "name": "Camion 3,5 t", "capacity": "pana la 3.500 kg", "base": 35, "per_km": 2.5, "per_min": 0.55, "speed_kmh": 24},
    {"id": "camion75", "service": "fracht", "name": "Camion 7,5 t", "capacity": "pana la 7.500 kg", "base": 60, "per_km": 3.2, "per_min": 0.75, "speed_kmh": 22},
]

# Zona de serviciu: Hamburg si imprejurimi, raza maxima 100 km.
SERVICE_CENTER = {"name": "Hamburg", "lat": 53.5511, "lng": 9.9937}
MAX_RADIUS_KM = 100

# Adrese simulate (coordonate reale) in zona Hamburg, toate in raza de 100 km.
# INLOCUIESTE IN PRODUCTIE: aici ar veni geocodarea adresei scrise de user.
LOCATIONS = [
    {"id": "hamburg_rathaus", "name": "Hamburg Rathaus (centru)", "lat": 53.5503, "lng": 9.9920},
    {"id": "hafencity", "name": "HafenCity", "lat": 53.5413, "lng": 10.0000},
    {"id": "altona", "name": "Altona", "lat": 53.5503, "lng": 9.9350},
    {"id": "flughafen", "name": "Aeroport Hamburg (Fuhlsbüttel)", "lat": 53.6304, "lng": 9.9882},
    {"id": "harburg", "name": "Harburg", "lat": 53.4600, "lng": 9.9830},
    {"id": "bergedorf", "name": "Bergedorf", "lat": 53.4890, "lng": 10.2120},
    {"id": "norderstedt", "name": "Norderstedt", "lat": 53.6860, "lng": 9.9800},
    {"id": "pinneberg", "name": "Pinneberg", "lat": 53.6560, "lng": 9.7990},
    {"id": "buxtehude", "name": "Buxtehude", "lat": 53.4766, "lng": 9.7000},
    {"id": "stade", "name": "Stade", "lat": 53.5930, "lng": 9.4760},
    {"id": "lueneburg", "name": "Lüneburg", "lat": 53.2500, "lng": 10.4140},
    {"id": "luebeck", "name": "Lübeck", "lat": 53.8655, "lng": 10.6866},
    {"id": "kiel", "name": "Kiel (~90 km)", "lat": 54.3233, "lng": 10.1228},
]

# Fluxul de stari al unei comenzi.
ORDER_FLOW = [
    {"id": "cautare_sofer", "label": "Se cauta sofer"},
    {"id": "acceptat", "label": "Acceptat de sofer"},
    {"id": "spre_ridicare", "label": "Soferul se indreapta spre ridicare"},
    {"id": "ridicat", "label": "Colet ridicat"},
    {"id": "in_livrare", "label": "In livrare"},
    {"id": "livrat", "label": "Livrat"},
]

# Soferi simulati.
DRIVERS = [
    {"id": "d1", "name": "Andrei M.", "vehicle": "masina", "rating": 4.9, "online": True},
    {"id": "d2", "name": "Ioana V.", "vehicle": "scuter", "rating": 4.8, "online": True},
    {"id": "d3", "name": "Radu P.", "vehicle": "transporter", "rating": 4.7, "online": True},
]


# --- Geometrie / distanta --------------------------------------------------

def haversine_km(a, b):
    R = 6371.0
    d_lat = radians(b["lat"] - a["lat"])
    d_lng = radians(b["lng"] - a["lng"])
    lat1, lat2 = radians(a["lat"]), radians(b["lat"])
    h = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lng / 2) ** 2
    return 2 * R * asin(sqrt(h))


def road_distance_km(a, b):
    """Distanta pe sosea ~ linie dreapta * 1.3 (factor orientativ de oras)."""
    return round(haversine_km(a, b) * 1.3, 1)


def within_service_area(point):
    return haversine_km(SERVICE_CENTER, point) <= MAX_RADIUS_KM


def quote_for_vehicle(vehicle, km):
    """Calculeaza pretul pentru un vehicul, pe baza distantei (reale) in km."""
    minutes = max(5, round((km / vehicle["speed_kmh"]) * 60))
    price = vehicle["base"] + vehicle["per_km"] * km + vehicle["per_min"] * minutes
    return {
        "vehicleId": vehicle["id"],
        "distanceKm": km,
        "etaMin": minutes,
        "price": round(price, 2),
    }


# --- Helperi de cautare ----------------------------------------------------

def find_location(loc_id):
    return next((l for l in LOCATIONS if l["id"] == loc_id), None)


def find_vehicle(veh_id):
    return next((v for v in VEHICLES if v["id"] == veh_id), None)


def find_driver(driver_id):
    return next((d for d in DRIVERS if d["id"] == driver_id), None)
