from django.core.management.base import BaseCommand

from delivery import taxonomy
from delivery.models import VehicleClass, Capability, Vertical


class Command(BaseCommand):
    help = "Incarca/actualizeaza taxonomia (clase, capabilitati, verticale) din delivery/taxonomy.json"

    def handle(self, *args, **opts):
        nc, ncap, nv = taxonomy.load(VehicleClass, Capability, Vertical)
        self.stdout.write(self.style.SUCCESS(
            f"Taxonomie sincronizata din taxonomy.json: {nc} clase, {ncap} capabilitati, {nv} verticale."))
