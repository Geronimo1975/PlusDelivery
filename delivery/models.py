from django.contrib.auth.models import User
from django.db import models

from . import data


class Profile(models.Model):
    """Date suplimentare peste User-ul Django: rolul (client/sofer) si campurile
    specifice fiecarui rol. Un User = un Profile (OneToOne)."""

    ROLE_CHOICES = [("client", "Client"), ("driver", "Sofer")]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="client")
    phone = models.CharField(max_length=40, blank=True)

    # Client business (companie care trimite multe livrari)
    is_business = models.BooleanField(default=False)
    company = models.CharField(max_length=120, blank=True)

    # Sofer
    vehicle_id = models.CharField(max_length=20, blank=True)
    rating = models.FloatField(default=5.0)
    online = models.BooleanField(default=False)

    def display_name(self):
        return self.user.get_full_name() or self.user.first_name or self.user.username

    def __str__(self):
        return f"{self.display_name()} ({self.get_role_display()})"


class Order(models.Model):
    """O comanda de livrare. Datele rutei sunt denormalizate (nume+coordonate)
    ca sa fie simplu de afisat fara alte interogari."""

    code = models.CharField(max_length=20, unique=True, blank=True)

    # Cine a creat comanda (client) si cine o livreaza (sofer). Null = demo/anonim.
    client = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")
    driver_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="jobs")

    service_type = models.CharField(max_length=20)
    vehicle_id = models.CharField(max_length=20)
    vehicle_name = models.CharField(max_length=60)

    from_id = models.CharField(max_length=40)
    from_name = models.CharField(max_length=80)
    from_lat = models.FloatField()
    from_lng = models.FloatField()

    to_id = models.CharField(max_length=40)
    to_name = models.CharField(max_length=80)
    to_lat = models.FloatField()
    to_lng = models.FloatField()

    note = models.CharField(max_length=300, blank=True)
    contact = models.CharField(max_length=60, blank=True)

    price = models.FloatField()
    distance_km = models.FloatField()
    eta_min = models.IntegerField()
    # Geometria traseului pe strazi (lista de puncte [lat, lng]) de la OSRM.
    route_geometry = models.JSONField(default=list, blank=True)
    # Opriri intermediare intre ridicare si livrare: [{name, lat, lng}].
    stops = models.JSONField(default=list, blank=True)

    status = models.CharField(max_length=20, default=data.ORDER_FLOW[0]["id"])

    driver_id = models.CharField(max_length=20, null=True, blank=True)
    driver_name = models.CharField(max_length=60, null=True, blank=True)
    driver_rating = models.FloatField(null=True, blank=True)
    driver_lat = models.FloatField(null=True, blank=True)
    driver_lng = models.FloatField(null=True, blank=True)

    progress = models.FloatField(default=0)
    # Nota data de client soferului dupa livrare (1..5), null pana la evaluare.
    rating = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Programare in avans: daca e setat si in viitor, comanda porneste in starea
    # "programat" si e promovata la "cautare_sofer" de ceas (realtime) la ora ei.
    scheduled_for = models.DateTimeField(null=True, blank=True)
    # Verticala (domeniu) a comenzii. Determina cerintele de vehicul/capabilitati
    # pentru matching. Null = comanda generica (fara cerinte speciale).
    vertical = models.ForeignKey("Vertical", null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name="orders")
    # Valorile campurilor specifice domeniului (dupa `Vertical.order_fields`),
    # ca {key: value}. Ex. pentru farmacie: {"reteta": "RX-123", "verif_id": true}.
    vertical_fields = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        creating = self._state.adding and not self.code
        super().save(*args, **kwargs)
        if creating and not self.code:
            self.code = f"PD-{1000 + self.id}"
            super().save(update_fields=["code"])

    def serialize(self):
        """Transforma comanda in dict-ul (camelCase) asteptat de frontend."""
        driver = None
        if self.driver_id:
            driver = {
                "id": self.driver_id,
                "name": self.driver_name,
                "rating": self.driver_rating,
                "phone": "+49 40 000000",  # simulat
            }
        driver_pos = None
        if self.driver_lat is not None and self.driver_lng is not None:
            driver_pos = {"lat": self.driver_lat, "lng": self.driver_lng}
        return {
            "id": self.code,
            "serviceType": self.service_type,
            "vehicleId": self.vehicle_id,
            "vehicleName": self.vehicle_name,
            "from": {"id": self.from_id, "name": self.from_name, "lat": self.from_lat, "lng": self.from_lng},
            "to": {"id": self.to_id, "name": self.to_name, "lat": self.to_lat, "lng": self.to_lng},
            "stops": self.stops or [],
            "note": self.note,
            "contact": self.contact,
            "price": self.price,
            "distanceKm": self.distance_km,
            "etaMin": self.eta_min,
            "status": self.status,
            "routeGeometry": self.route_geometry or [],
            "rating": self.rating,
            "driver": driver,
            "driverPos": driver_pos,
            "progress": self.progress,
            "createdAt": int(self.created_at.timestamp() * 1000) if self.created_at else None,
            "scheduledFor": int(self.scheduled_for.timestamp() * 1000) if self.scheduled_for else None,
            "vertical": self.vertical.slug if self.vertical_id else None,
            "verticalName": self.vertical.name if self.vertical_id else None,
            "verticalFields": self.vertical_fields or {},
            "requires": self._requires(),
        }

    def _requires(self):
        """Cerintele de vehicul pentru matching, derivate din verticala.
        None = comanda generica, acceptata de orice vehicul."""
        if not self.vertical_id:
            return None
        v = self.vertical
        return {
            "minRank": v.min_vehicle_class.rank if v.min_vehicle_class_id else 0,
            "caps": list(v.required_capabilities.values_list("slug", flat=True)),
        }

    def __str__(self):
        return f"{self.code or '(nou)'} · {self.from_name} → {self.to_name}"


# ===========================================================================
# Taxonomia multi-verticala: clase de vehicul + capabilitati + domenii.
#
# Doua axe INDEPENDENTE descriu un transport:
#   - VehicleClass : cat duce (tonaj / volum), cu un `rank` pentru comparatii.
#   - Capability   : in ce conditii (frigorific, izoterm, farma, bio, ...).
# Un vehicul real al unui transportator = o clasa + 0..N capabilitati dovedite.
# O verticala (domeniu) cere: o clasa minima + un set de capabilitati + licente.
# Matching-ul = clasa suficienta ∩ capabilitati ⊇ cerinte ∩ vehicul verificat.
#
# Model aditiv: NU inlocuieste inca `data.VEHICLES`/`Order.vehicle_id`. Scopul
# acestei etape e sa vedem taxonomia "in realitate" (in admin) si sa o ajustam.
# ===========================================================================


class VehicleClass(models.Model):
    """Clasa de vehicul dupa tonaj si volum (ex: scuter, duba, camion 7,5t)."""
    slug = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    max_weight_kg = models.PositiveIntegerField(help_text="Greutate maxima transportabila (kg).")
    volume_m3 = models.FloatField(null=True, blank=True, help_text="Volum orientativ (m³), optional.")
    # Rang crescator dupa capacitate; folosit pentru 'clasa >= clasa minima ceruta'.
    rank = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["rank"]
        verbose_name = "Clasa vehicul"
        verbose_name_plural = "Clase vehicul"

    def __str__(self):
        return f"{self.name} (≤{self.max_weight_kg} kg)"


class Capability(models.Model):
    """Tip de transport / conditie pe care un vehicul o poate asigura."""
    slug = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=200, blank=True)
    # Daca e True, capabilitatea se activeaza doar cu document/licenta valid(a).
    needs_document = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
        verbose_name = "Capabilitate"
        verbose_name_plural = "Capabilitati"

    def __str__(self):
        return self.name


class Vertical(models.Model):
    """Un domeniu de livrare (mancare, farmacie, materiale biologice, ...).
    Nu e cod nou, ci o configuratie citita de platforma."""
    slug = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=240, blank=True)
    active = models.BooleanField(default=True)

    min_vehicle_class = models.ForeignKey(
        VehicleClass, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="verticals_min",
        help_text="Clasa minima acceptata (dupa rank). Gol = orice clasa.")
    required_capabilities = models.ManyToManyField(
        Capability, blank=True, related_name="verticals",
        help_text="Capabilitati obligatorii pentru acest domeniu.")
    required_licenses = models.JSONField(
        default=list, blank=True,
        help_text='Licente/autorizatii cerute, ca lista de siruri (ex: ["ADR"]).')
    # Campuri specifice adaugate la formularul de comanda, ca lista de dict-uri
    # {key, label, type, required}. Ex: {"key":"temp","label":"Temperatura","type":"number"}.
    order_fields = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Verticala (domeniu)"
        verbose_name_plural = "Verticale (domenii)"

    def __str__(self):
        return self.name

    def eligible_vehicles(self):
        """Vehiculele verificate care pot deservi aceasta verticala."""
        qs = TransporterVehicle.objects.filter(active=True, verified=True)
        if self.min_vehicle_class_id:
            min_rank = self.min_vehicle_class.rank
            qs = qs.filter(vehicle_class__rank__gte=min_rank)
        for cap in self.required_capabilities.all():
            qs = qs.filter(capabilities=cap)
        return qs.distinct()

    def accepts_vehicle(self, vehicle):
        """True daca `vehicle` indeplineste clasa + capabilitatile cerute."""
        if not (vehicle.active and vehicle.verified):
            return False
        if self.min_vehicle_class_id and vehicle.vehicle_class.rank < self.min_vehicle_class.rank:
            return False
        have = set(vehicle.capabilities.values_list("id", flat=True))
        need = set(self.required_capabilities.values_list("id", flat=True))
        return need.issubset(have)


class TransporterVehicle(models.Model):
    """Vehiculul inregistrat de un transportator. El declara clasa + capabilitatile
    si ISI ASUMA RASPUNDEREA pentru tipul de transport; platforma verifica."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vehicles")
    vehicle_class = models.ForeignKey(VehicleClass, on_delete=models.PROTECT, related_name="vehicles")
    capabilities = models.ManyToManyField(Capability, blank=True, related_name="vehicles")

    label = models.CharField(max_length=80, blank=True, help_text="Ex: VW Caddy alb.")
    plate = models.CharField(max_length=20, blank=True, help_text="Numar de inmatriculare.")
    # Documente doveditoare: lista de {type, ref, expires} (ISO). Ex: autorizatie ADR.
    documents = models.JSONField(default=list, blank=True)

    responsibility_accepted = models.BooleanField(
        default=False, help_text="Transportatorul si-a asumat raspunderea pentru acest transport.")
    verified = models.BooleanField(default=False, help_text="Verificat de platforma (documente OK).")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "Vehicul transportator"
        verbose_name_plural = "Vehicule transportator"

    def __str__(self):
        who = self.owner.get_username()
        return f"{self.label or self.vehicle_class.name} · {who}"
