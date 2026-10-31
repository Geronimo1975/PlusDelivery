from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from dashboard.authorization import permissions, services


class PermissionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("u1", password="x")
        self.admin = User.objects.create_user("adm", password="x")

    def test_can_order_requires_verified(self):
        self.assertFalse(permissions.can_order(self.user))
        services.confirm_account(self.user)
        self.assertTrue(permissions.can_order(self.user))

    def test_can_drive_requires_verified_and_approved(self):
        app = services.submit_driver_application(self.user)
        self.assertFalse(permissions.can_drive(self.user))
        services.approve_driver(app, self.admin)
        self.assertFalse(permissions.can_drive(self.user))  # approved but unverified
        services.confirm_account(self.user)
        self.assertTrue(permissions.can_drive(self.user))
        app.refresh_from_db()
        self.assertEqual(app.reviewed_by, self.admin)
        self.assertIsNotNone(app.reviewed_at)

    def test_anonymous(self):
        self.assertFalse(permissions.is_verified(AnonymousUser()))
        self.assertFalse(permissions.can_drive(AnonymousUser()))

    def test_drf_classes_and_decorator(self):
        req = RequestFactory().get("/")
        req.user = self.user
        self.assertFalse(permissions.IsVerified().has_permission(req, None))
        self.assertFalse(permissions.IsDriverApproved().has_permission(req, None))
        services.confirm_account(self.user)
        self.assertTrue(permissions.IsVerified().has_permission(req, None))

        view = permissions.require_verified(lambda r: HttpResponse("ok"))
        req.user = User.objects.create_user("u2", password="x")
        self.assertEqual(view(req).status_code, 403)
        req.user = self.user
        self.assertEqual(view(req).status_code, 200)


class DriverApplicationHelperTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("h1", password="x")
        self.admin = User.objects.create_user("hadm", password="x")

    def test_has_driver_application_pending_and_none(self):
        self.assertFalse(permissions.has_driver_application(self.user))
        services.submit_driver_application(self.user)
        self.assertTrue(permissions.has_driver_application(self.user))

    def test_has_driver_application_excludes_rejected(self):
        from dashboard.authorization.models import DriverApplication

        app = services.submit_driver_application(self.user)
        app.status = DriverApplication.Status.REJECTED
        app.save()
        self.assertFalse(permissions.has_driver_application(self.user))

    def test_pending_applications_only_pending(self):
        other = User.objects.create_user("h2", password="x")
        services.submit_driver_application(self.user)
        done = services.submit_driver_application(other)
        services.approve_driver(done, self.admin)
        self.assertEqual([a.user for a in services.pending_applications()], [self.user])
