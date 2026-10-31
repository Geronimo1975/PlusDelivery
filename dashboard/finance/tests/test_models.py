from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase

from dashboard.accounts.models import Organization
from dashboard.finance import services
from dashboard.finance.models import Wallet


class WalletTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="x")
        self.org = Organization.objects.create(name="Acme", owner=self.user)

    def test_wallet_requires_exactly_one_owner(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Wallet.objects.create(user=self.user, organization=self.org)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Wallet.objects.create()

    def test_wallet_for_routes_by_owner_and_is_idempotent(self):
        w1 = services.wallet_for(user=self.user)
        w2 = services.wallet_for(organization=self.org)
        self.assertEqual(w1.user, self.user)
        self.assertIsNone(w1.organization)
        self.assertEqual(w2.organization, self.org)
        self.assertIsNone(w2.user)
        self.assertEqual(services.wallet_for(user=self.user).pk, w1.pk)
        with self.assertRaises(ValueError):
            services.wallet_for()
        with self.assertRaises(ValueError):
            services.wallet_for(user=self.user, organization=self.org)

    def test_record_transaction_updates_balance(self):
        w = services.wallet_for(user=self.user)
        services.record_transaction(w, Decimal("50.00"), "credit")
        services.record_transaction(w, Decimal("12.50"), "debit", order_code="PD-1")
        w.refresh_from_db()
        self.assertEqual(w.balance, Decimal("37.50"))
        self.assertEqual(w.transactions.count(), 2)

    def test_record_transaction_rejects_bad_input(self):
        w = services.wallet_for(user=self.user)
        with self.assertRaises(ValueError):
            services.record_transaction(w, Decimal("1"), "bogus")
        with self.assertRaises(ValueError):
            services.record_transaction(w, Decimal("-1"), "credit")
