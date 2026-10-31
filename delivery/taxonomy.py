"""Incarcator pentru taxonomia multi-verticala.

Sursa de adevar textuala e `taxonomy.json` (clase, capabilitati, verticale).
`load()` o aplica idempotent (update_or_create), deci poate fi re-rulata ori de
cate ori editezi fisierul. E folosita atat de migratia de seed, cat si de
comanda de management `load_taxonomy`. Nu importa modele la nivel de modul, ca
sa poata fi chemata si din migratii (cu modele istorice via apps.get_model)."""
import json
import os

_PATH = os.path.join(os.path.dirname(__file__), "taxonomy.json")


def read_config(path=None):
    with open(path or _PATH, encoding="utf-8") as fh:
        return json.load(fh)


def load(VehicleClass, Capability, Vertical, config=None):
    """Upsert idempotent al taxonomiei. Returneaza (n_clase, n_capab, n_verticale)."""
    data = config or read_config()

    cls_by = {}
    for c in data.get("classes", []):
        obj, _ = VehicleClass.objects.update_or_create(
            slug=c["slug"],
            defaults={"name": c["name"], "max_weight_kg": c["max_weight_kg"],
                      "volume_m3": c.get("volume_m3"), "rank": c.get("rank", 0), "active": True})
        cls_by[c["slug"]] = obj

    cap_by = {}
    for c in data.get("capabilities", []):
        obj, _ = Capability.objects.update_or_create(
            slug=c["slug"],
            defaults={"name": c["name"], "description": c.get("description", ""),
                      "needs_document": c.get("needs_document", False)})
        cap_by[c["slug"]] = obj

    for v in data.get("verticals", []):
        obj, _ = Vertical.objects.update_or_create(
            slug=v["slug"],
            defaults={"name": v["name"], "description": v.get("description", ""), "active": True,
                      "min_vehicle_class": cls_by.get(v.get("min_class")),
                      "required_licenses": v.get("licenses", []),
                      "order_fields": v.get("order_fields", [])})
        obj.required_capabilities.set([cap_by[s] for s in v.get("capabilities", []) if s in cap_by])

    return len(cls_by), len(cap_by), len(data.get("verticals", []))


def slugs(config=None):
    """Slug-urile definite in config, pe categorii (pentru stergere la revert)."""
    data = config or read_config()
    return {
        "classes": [c["slug"] for c in data.get("classes", [])],
        "capabilities": [c["slug"] for c in data.get("capabilities", [])],
        "verticals": [v["slug"] for v in data.get("verticals", [])],
    }
