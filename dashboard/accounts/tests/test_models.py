from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase

from dashboard.accounts import services
from dashboard.accounts.models import AccountProfile, Membership, Organization


class AccountsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="x")
        self.org = Organization.objects.create(name="Acme", owner=self.user)

    def test_membership_unique(self):
        Membership.objects.create(user=self.user, organization=self.org, role=Membership.Role.ADMIN)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Membership.objects.create(user=self.user, organization=self.org, role=Membership.Role.EMPLOYEE)

    def test_default_account_type(self):
        self.assertEqual(services.get_account_type(self.user), "personal")
        AccountProfile.objects.create(user=self.user, account_type=AccountProfile.AccountType.BUSINESS)
        self.assertEqual(services.get_account_type(self.user), "business")

    def test_organizations_for_returns_member_orgs(self):
        other = Organization.objects.create(name="Other", owner=self.user)
        bob = User.objects.create_user("bob", password="x")
        Membership.objects.create(user=bob, organization=self.org, role=Membership.Role.MANAGER)
        self.assertEqual(list(services.organizations_for(bob)), [self.org])
        self.assertNotIn(other, services.organizations_for(bob))
