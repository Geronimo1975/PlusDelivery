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
        }

    def __str__(self):
        return f"{self.code or '(nou)'} · {self.from_name} → {self.to_name}"
