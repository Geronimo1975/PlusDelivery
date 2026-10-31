"""Leaga poarta de verificare (dashboard.authorization) de vehiculele curierului.

Cand o DriverApplication devine 'approved', vehiculele transportatorului devin
`verified=True` (si pot fi oferite la matching); daca nu e aprobata, raman
neverificate. Astfel aprobarea reala (admin/poarta), nu o auto-aprobare, decide
ce vehicule intra in matching."""
from django.db.models.signals import post_save


def _on_driver_application_saved(sender, instance, **kwargs):
    from .models import TransporterVehicle
    approved = instance.status == sender.Status.APPROVED
    TransporterVehicle.objects.filter(owner_id=instance.user_id).update(verified=approved)


def connect():
    """Conecteaza semnalele. Chemat din DeliveryConfig.ready() in orice proces."""
    from dashboard.authorization.models import DriverApplication
    post_save.connect(
        _on_driver_application_saved,
        sender=DriverApplication,
        dispatch_uid="delivery.verify_vehicles_on_driver_approval",
    )
