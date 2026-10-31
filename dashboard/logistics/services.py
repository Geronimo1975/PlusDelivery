"""Strat de servicii peste delivery.Order (legacy core, doar citire/import)."""
from django.core.exceptions import PermissionDenied

from dashboard.authorization import permissions
from delivery.models import Order


def all_orders():
    return Order.objects.all()


def orders_for_dispatch():
    """Comenzi fara sofer asignat."""
    return Order.objects.filter(driver_user__isnull=True)


def place_order_guard(user):
    if not permissions.can_order(user):
        raise PermissionDenied("Account not verified.")
