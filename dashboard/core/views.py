"""Modulul `core`: poarta de validare + rutare pe roluri + dashboard Admin/Operational."""
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from dashboard.accounts import services as account_services
from dashboard.accounts.models import AccountProfile
from dashboard.authorization import permissions
from dashboard.authorization import services as auth_services
from dashboard.authorization.models import DriverApplication
from dashboard.logistics import services as logistics_services

staff_required = user_passes_test(lambda u: u.is_staff)


def _role_for(user) -> str:
    """Determina rolul operational pentru rutare: driver > business > client."""
    if permissions.can_drive(user) or DriverApplication.objects.filter(user=user).exists():
        return "driver"
    if account_services.get_account_type(user) == AccountProfile.AccountType.BUSINESS.value:
        return "business"
    return "client"


@login_required
def home(request):
    """Ruteaza pe rol: staff -> dashboard admin; altfel -> stub-ul rolului."""
    if request.user.is_staff:
        return redirect("dashboard:admin_home")
    role = _role_for(request.user)
    context = {
        "role": role,
        "verified": permissions.is_verified(request.user),
        "can_drive": permissions.can_drive(request.user),
        "organizations": account_services.organizations_for(request.user),
    }
    return render(request, "dashboard/home.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def gate(request):
    """Poarta de validare: GET afiseaza bannerul; POST (action=confirm) -> confirm_account."""
    if request.method == "POST" and request.POST.get("action") == "confirm":
        auth_services.confirm_account(request.user, via="stub")
        return redirect("dashboard:home")
    return render(request, "dashboard/gate.html", {"verified": permissions.is_verified(request.user)})


@login_required
@require_http_methods(["POST"])
def driver_apply(request):
    """Trimite o aplicatie de sofer. Guard: contul trebuie validat. Prinde IntegrityError (aplicatie activa duplicata)."""
    if not permissions.is_verified(request.user):
        return redirect("dashboard:gate")
    try:
        # Savepoint, astfel incat IntegrityError (aplicatie activa duplicata) sa nu rupa tranzactia.
        with transaction.atomic():
            auth_services.submit_driver_application(request.user)
        messages_text = "Deine Fahrer-Bewerbung wurde eingereicht."
    except IntegrityError:
        messages_text = "Du hast bereits eine aktive Fahrer-Bewerbung."
    response = redirect("dashboard:home")
    response["X-PlusDelivery-Message"] = messages_text
    return response


@login_required
@staff_required
def admin_home(request):
    """Dashboard Admin/Operational: comenzi + coada aplicatiilor de sofer in asteptare."""
    context = {
        "orders": logistics_services.all_orders().order_by("-created_at")[:50],
        "dispatch_orders": logistics_services.orders_for_dispatch()[:50],
        "pending_applications": DriverApplication.objects.filter(
            status=DriverApplication.Status.PENDING
        ).select_related("user").order_by("submitted_at"),
    }
    return render(request, "dashboard/admin.html", context)


@login_required
@staff_required
@require_http_methods(["POST"])
def approve_driver(request):
    """Aproba o aplicatie de sofer aflata in starea `pending` (guard inainte de approve_driver)."""
    application_id = request.POST.get("application_id")
    application = get_object_or_404(DriverApplication, pk=application_id)
    if application.status == DriverApplication.Status.PENDING:
        auth_services.approve_driver(application, request.user)
    return redirect("dashboard:admin_home")
