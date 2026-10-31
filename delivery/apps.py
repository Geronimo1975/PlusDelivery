import os
import sys

from django.apps import AppConfig


class DeliveryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "delivery"

    def ready(self):
        # Semnalele se inregistreaza in ORICE proces (inclusiv Daphne), inainte
        # de guard-ul de simulare de mai jos.
        from . import signals
        signals.connect()

        # Pornim simularea doar in procesul care serveste efectiv cererile.
        if "runserver" not in sys.argv:
            return
        # Sub auto-reload, procesul care serveste are RUN_MAIN='true'.
        if os.environ.get("RUN_MAIN") != "true":
            return
        from .simulation import start_simulation
        start_simulation()
