from functools import wraps

from django.http import HttpResponseForbidden
from rest_framework.permissions import BasePermission

from .models import AccountVerification, DriverApplication


def is_verified(user):
    if not user or not user.is_authenticated:
        return False
    return AccountVerification.objects.filter(user=user, is_verified=True).exists()


def can_order(user):
    return is_verified(user)


def can_drive(user):
    return is_verified(user) and DriverApplication.objects.filter(
        user=user, status=DriverApplication.Status.APPROVED
    ).exists()


def has_driver_application(user):
    """True daca utilizatorul are o aplicatie de sofer activa (pending/approved); respinsele nu conteaza."""
    return DriverApplication.objects.filter(user=user).exclude(
        status=DriverApplication.Status.REJECTED
    ).exists()


class IsVerified(BasePermission):
    message = "Account not verified."

    def has_permission(self, request, view):
        return is_verified(request.user)


class IsDriverApproved(BasePermission):
    message = "Driver application not approved."

    def has_permission(self, request, view):
        return can_drive(request.user)


def require_verified(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not is_verified(request.user):
            return HttpResponseForbidden("Account not verified.")
        return view(request, *args, **kwargs)

    return wrapper
