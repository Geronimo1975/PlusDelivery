import os
import sys

from django.apps import AppConfig


class DeliveryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "delivery"

    def ready(self):
        # Pornim simularea doar in procesul care serveste efectiv cererile.
        if "runserver" not in sys.argv:
            return
        # Sub auto-reload, procesul care serveste are RUN_MAIN='true'.
        if os.environ.get("RUN_MAIN") != "true":
            return
        from .simulation import start_simulation
        start_simulation()
