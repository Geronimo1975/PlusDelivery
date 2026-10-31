from django.contrib.auth.models import User
from django.db import models


class AccountProfile(models.Model):
    """Tipul de cont al unui utilizator (personal/business/premium)."""

    class AccountType(models.TextChoices):
        PERSONAL = "personal", "Personal"
        BUSINESS = "business", "Business"
        PREMIUM = "premium", "Premium"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="account_profile")
    account_type = models.CharField(max_length=10, choices=AccountType.choices, default=AccountType.PERSONAL)

    def __str__(self):
        return f"{self.user.username} ({self.account_type})"


class Organization(models.Model):
    name = models.CharField(max_length=120)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="owned_organizations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        EMPLOYEE = "employee", "Employee"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.EMPLOYEE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "organization"], name="unique_user_organization"),
        ]

    def __str__(self):
        return f"{self.user.username} @ {self.organization.name} ({self.role})"
