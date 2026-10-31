from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from axes.utils import reset


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class LoginSecurityTests(TestCase):
    """Rate-limiting login prin django-axes (testat pe admin login, care trece prin backend-urile de auth)."""

    def setUp(self):
        reset()
        User = get_user_model()
        User.objects.create_user(
            username="staff1", password="s3cret-Pass!", is_staff=True, is_superuser=True
        )
        self.url = reverse("admin:login")

    def tearDown(self):
        reset()

    def _post(self, password):
        return self.client.post(
            self.url,
            {"username": "staff1", "password": password, "next": "/admin/"},
            REMOTE_ADDR="10.0.0.1",
        )

    def test_lockout_after_failed_attempts(self):
        limit = settings.AXES_FAILURE_LIMIT
        for _ in range(limit - 1):
            self.assertEqual(self._post("wrong").status_code, 200)
        # A limit-a incercare esuata declanseaza blocarea.
        self.assertEqual(self._post("wrong").status_code, 429)
        # Chiar si parola corecta e refuzata cat timp contul e blocat.
        self.assertEqual(self._post("s3cret-Pass!").status_code, 429)

    def test_valid_login_before_limit_ok(self):
        for _ in range(2):
            self.assertEqual(self._post("wrong").status_code, 200)
        resp = self._post("s3cret-Pass!")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], "/admin/")
