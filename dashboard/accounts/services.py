from .models import AccountProfile, Organization


def get_account_type(user) -> str:
    """Tipul contului; 'personal' daca nu exista profil."""
    profile = AccountProfile.objects.filter(user=user).only("account_type").first()
    return profile.account_type if profile else AccountProfile.AccountType.PERSONAL.value


def organizations_for(user):
    """Organizatiile in care utilizatorul este membru."""
    return Organization.objects.filter(memberships__user=user).distinct()
