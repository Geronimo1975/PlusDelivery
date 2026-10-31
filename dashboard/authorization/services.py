from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import AccountVerification, DriverApplication


def confirm_account(user, via="stub"):
    verification, _ = AccountVerification.objects.get_or_create(user=user)
    verification.is_verified = True
    verification.verified_via = via
    verification.verified_at = timezone.now()
    verification.save()
    return verification


def submit_driver_application(user):
    return DriverApplication.objects.create(user=user)


def approve_driver(application, reviewer):
    application.status = DriverApplication.Status.APPROVED
    application.reviewed_by = reviewer
    application.reviewed_at = timezone.now()
    application.save(update_fields=["status", "reviewed_by", "reviewed_at"])


def pending_applications():
    """Aplicatiile de sofer in asteptare, cele mai vechi primele."""
    return (
        DriverApplication.objects.filter(status=DriverApplication.Status.PENDING)
        .select_related("user")
        .order_by("submitted_at")
    )


def approve_pending_application(application_id, reviewer):
    """Aproba aplicatia daca exista si este `pending` (404 daca lipseste; no-op altfel)."""
    application = get_object_or_404(DriverApplication, pk=application_id)
    if application.status == DriverApplication.Status.PENDING:
        approve_driver(application, reviewer)
    return application
