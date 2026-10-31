from django.db import migrations

# Seed-ul taxonomiei citeste din delivery/taxonomy.json (sursa textuala, editabila).
# Idempotent (update_or_create) si reversibil. Dupa editarea JSON, re-aplica fie cu
# `python manage.py load_taxonomy`, fie printr-o migratie noua de date.
from delivery import taxonomy


def seed(apps, schema_editor):
    taxonomy.load(
        apps.get_model("delivery", "VehicleClass"),
        apps.get_model("delivery", "Capability"),
        apps.get_model("delivery", "Vertical"),
    )


def unseed(apps, schema_editor):
    s = taxonomy.slugs()
    apps.get_model("delivery", "Vertical").objects.filter(slug__in=s["verticals"]).delete()
    apps.get_model("delivery", "Capability").objects.filter(slug__in=s["capabilities"]).delete()
    apps.get_model("delivery", "VehicleClass").objects.filter(slug__in=s["classes"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("delivery", "0007_capability_vehicleclass_transportervehicle_vertical"),
    ]
    operations = [migrations.RunPython(seed, unseed)]
