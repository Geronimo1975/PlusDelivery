# ---------------------------------------------------------------------------
# Autentificare (sesiuni Django) pentru cele doua roluri: client si sofer.
# Model inspirat de Lalamove: portaluri separate "Für Benutzer" (clienti) si
# "Für Fahrer" (soferi), fiecare cu inregistrare + login. Clientul poate fi si
# "business" (companie care trimite multe livrari).
#
# Protectie CSRF ACTIVA: cererile POST au nevoie de antetul X-CSRFToken (frontend-ul
# il trimite din cookie-ul csrftoken). Pagina seteaza cookie-ul prin @ensure_csrf_cookie.
# INLOCUIESTE IN PRODUCTIE: verificare email, resetare parola, politici de parola,
# rate limiting la login; eventual token-uri (ex. JWT) daca API-ul devine fara stare.
# ---------------------------------------------------------------------------
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse

from . import data
from .models import Profile


def _body(request):
    try:
        return json.loads(request.body or "{}")
    except (ValueError, TypeError):
        return {}


def user_payload(user):
    """Datele utilizatorului trimise catre frontend (fara parola)."""
    if not user or not user.is_authenticated:
        return {"authenticated": False}
    p = getattr(user, "profile", None)
    if p is None:
        p = Profile.objects.create(user=user)
    veh = data.find_vehicle(p.vehicle_id) if p.vehicle_id else None
    return {
        "authenticated": True,
        "name": p.display_name(),
        "email": user.email,
        "role": p.role,
        "isBusiness": p.is_business,
        "company": p.company,
        "phone": p.phone,
        "vehicleId": p.vehicle_id,
        "vehicleName": veh["name"] if veh else "",
        "rating": p.rating,
        "online": p.online,
    }


def me(request):
    return JsonResponse(user_payload(request.user))


def register(request):
    b = _body(request)
    name = (b.get("name") or "").strip()
    email = (b.get("email") or "").strip().lower()
    password = b.get("password") or ""
    role = b.get("role") if b.get("role") in ("client", "driver") else "client"

    if not name or not email or len(password) < 6:
        return JsonResponse({"error": "Nume, email si parola (min. 6 caractere) sunt obligatorii."}, status=400)
    if User.objects.filter(username=email).exists():
        return JsonResponse({"error": "Exista deja un cont cu acest email."}, status=409)

    vehicle_id = ""
    if role == "driver":
        veh = data.find_vehicle(b.get("vehicleId"))
        if not veh:
            return JsonResponse({"error": "Alege un tip de vehicul."}, status=400)
        vehicle_id = veh["id"]

    user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
    Profile.objects.create(
        user=user,
        role=role,
        phone=b.get("phone", ""),
        is_business=bool(b.get("isBusiness")) if role == "client" else False,
        company=(b.get("company", "") if role == "client" else ""),
        vehicle_id=vehicle_id,
        online=(role == "driver"),  # soferul porneste online, poate comuta
    )
    # Cu django-axes exista mai multe backend-uri de autentificare; la register
    # userul nu vine din authenticate(), deci specificam explicit backend-ul.
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return JsonResponse(user_payload(user), status=201)


def login_view(request):
    b = _body(request)
    email = (b.get("email") or "").strip().lower()
    password = b.get("password") or ""
    user = authenticate(request, username=email, password=password)
    if user is None:
        return JsonResponse({"error": "Email sau parola gresita."}, status=401)
    login(request, user)
    return JsonResponse(user_payload(user))


def logout_view(request):
    logout(request)
    return JsonResponse({"authenticated": False})
