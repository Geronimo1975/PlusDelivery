"""Matching comanda ↔ transportator.

O comanda poate cere (prin verticala ei) o clasa minima de vehicul si un set de
capabilitati. Un transportator e eligibil daca vehiculul lui verificat are rang
suficient si include toate capabilitatile cerute. Comenzile fara cerinte
(`requires` None) sunt vizibile oricui."""


def eligible(requires, rank, caps):
    """Functie pura: `requires` (dict {minRank, caps} sau None) vs profilul
    vehiculului (`rank` int sau None, `caps` set/list de slug-uri)."""
    if not requires:
        return True
    if rank is None:
        return False
    if rank < requires.get("minRank", 0):
        return False
    return set(requires.get("caps", [])).issubset(set(caps or []))


def driver_profile(user):
    """Profilul de transport al unui curier: (rank, set(capabilitati)) din
    vehiculul lui activ si verificat; (None, set()) daca nu are unul."""
    from .models import TransporterVehicle
    v = (TransporterVehicle.objects
         .filter(owner=user, active=True, verified=True)
         .select_related("vehicle_class")
         .order_by("-id").first())
    if not v:
        return None, set()
    return v.vehicle_class.rank, set(v.capabilities.values_list("slug", flat=True))
