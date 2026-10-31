from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from dashboard.authorization import permissions
from dashboard.authorization.models import DriverApplication
from dashboard.authorization.services import confirm_account


class AdminHomeTests(TestCase):
    def test_admin_home_forbidden_for_non_staff(self):
        User.objects.create_user("bob", password="pw12345!")
        self.client.force_login(User.objects.get(username="bob"))
        resp = self.client.get(reverse("dashboard:admin_home"))
        self.assertIn(resp.status_code, (302, 403))

    def test_admin_home_ok_for_staff(self):
        User.objects.create_user("boss", password="pw12345!", is_staff=True)
        self.client.force_login(User.objects.get(username="boss"))
        resp = self.client.get(reverse("dashboard:admin_home"))
        self.assertEqual(resp.status_code, 200)


class GateTests(TestCase):
    def test_gate_post_confirms(self):
        user = User.objects.create_user("carol", password="pw12345!")
        self.client.force_login(User.objects.get(username="carol"))
        self.assertFalse(permissions.is_verified(user))
        resp = self.client.post(reverse("dashboard:gate"), {"action": "confirm"})
        self.assertIn(resp.status_code, (302, 200))
        self.assertTrue(permissions.is_verified(user))


class DriverApplyTests(TestCase):
    def test_driver_apply_blocked_when_unverified(self):
        User.objects.create_user("dan", password="pw12345!")
        self.client.force_login(User.objects.get(username="dan"))
        resp = self.client.post(reverse("dashboard:driver_apply"))
        self.assertIn(resp.status_code, (302, 403))
        self.assertFalse(
            DriverApplication.objects.filter(user__username="dan").exists()
        )

    def test_driver_apply_duplicate_shows_friendly_message(self):
        user = User.objects.create_user("erin", password="pw12345!")
        confirm_account(user, via="stub")
        DriverApplication.objects.create(user=user)
        self.client.force_login(User.objects.get(username="erin"))
        # Second submission must not 500 (IntegrityError caught).
        resp = self.client.post(reverse("dashboard:driver_apply"), follow=True)
        self.assertIn(resp.status_code, (200, 302))


class ApproveDriverTests(TestCase):
    def test_approve_driver_sets_approved(self):
        staff = User.objects.create_user("admin1", password="pw12345!", is_staff=True)
        applicant = User.objects.create_user("frank", password="pw12345!")
        confirm_account(applicant, via="stub")
        app = DriverApplication.objects.create(user=applicant)
        self.client.force_login(User.objects.get(username="admin1"))
        resp = self.client.post(
            reverse("dashboard:approve_driver"), {"application_id": app.id}
        )
        self.assertIn(resp.status_code, (302, 200))
        app.refresh_from_db()
        self.assertEqual(app.status, DriverApplication.Status.APPROVED)
        self.assertEqual(app.reviewed_by, staff)
