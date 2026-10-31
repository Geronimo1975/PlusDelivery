from django.conf import settings
from django.db import models
from django.db.models import Q


class AccountVerification(models.Model):
    """Poarta de 'confirmare unică'. verified_via: 'stub' acum; viitor google/facebook/linkedin."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="verification")
    is_verified = models.BooleanField(default=False)
    verified_via = models.CharField(max_length=20, default="", blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} verified={self.is_verified}"


class DriverApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="driver_applications")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_driver_applications"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(status__in=["pending", "approved"]),
                name="uniq_active_driver_application_per_user",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.status}"
