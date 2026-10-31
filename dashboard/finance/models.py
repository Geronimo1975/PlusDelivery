from django.conf import settings
from django.db import models
from django.db.models import Q


class Wallet(models.Model):
    """Portofel polimorf: apartine EXACT unui User (personal) SAU unei Organization (echipa)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="wallet"
    )
    organization = models.OneToOneField(
        "accounts.Organization", null=True, blank=True, on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(Q(user__isnull=False) & Q(organization__isnull=True))
                | (Q(user__isnull=True) & Q(organization__isnull=False)),
                name="wallet_exactly_one_owner",
            )
        ]

    def __str__(self):
        return f"Wallet({self.user or self.organization}: {self.balance})"


class Transaction(models.Model):
    class Kind(models.TextChoices):
        CREDIT = "credit", "Credit"
        DEBIT = "debit", "Debit"

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    kind = models.CharField(max_length=6, choices=Kind.choices)
    order_code = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]


class Statement(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="statements")
    period_start = models.DateField()
    period_end = models.DateField()

    class Meta:
        ordering = ["-period_end"]


class DriverEarning(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="driver_earnings")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    order_code = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
