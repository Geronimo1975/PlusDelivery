from django.apps import apps
from django.test import SimpleTestCase
from django.urls import reverse

LABELS = ["authorization", "accounts", "finance", "logistics", "core"]


class ScaffoldTests(SimpleTestCase):
    def test_apps_loaded(self):
        for label in LABELS:
            cfg = apps.get_app_config(label)
            self.assertEqual(cfg.name, f"dashboard.{label}")

    def test_dashboard_url_resolves(self):
        self.assertTrue(reverse("dashboard:home").startswith("/dashboard/"))
