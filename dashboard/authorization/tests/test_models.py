from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase

from dashboard.authorization import services
from dashboard.authorization.models import DriverApplication


class AuthorizationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("u1", password="x")

    def test_confirm_sets_flags(self):
        v = services.confirm_account(self.user)
        self.assertTrue(v.is_verified)
        self.assertEqual(v.verified_via, "stub")
        self.assertIsNotNone(v.verified_at)
        # idempotent
        v2 = services.confirm_account(self.user, via="google")
        self.assertEqual(v.pk, v2.pk)
        self.assertEqual(v2.verified_via, "google")

    def test_duplicate_active_application_rejected(self):
        services.submit_driver_application(self.user)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DriverApplication.objects.create(user=self.user)

    def test_rejected_application_allows_new_one(self):
        app = services.submit_driver_application(self.user)
        app.status = DriverApplication.Status.REJECTED
        app.save()
        self.assertEqual(services.submit_driver_application(self.user).status, "pending")
