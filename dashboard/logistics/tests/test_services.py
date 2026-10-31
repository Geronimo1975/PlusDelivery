from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from dashboard.authorization import services as auth_services
from dashboard.logistics import services
from delivery.models import Order


def make_order(driver=None, **kw):
    fields = dict(
        service_type="colet", vehicle_id="v1", vehicle_name="Van",
        from_id="a", from_name="A", from_lat=0.0, from_lng=0.0,
        to_id="b", to_name="B", to_lat=1.0, to_lng=1.0,
        price=10.0, distance_km=5.0, eta_min=15, driver_user=driver,
    )
    fields.update(kw)
    return Order.objects.create(**fields)


class LogisticsServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("u1", password="x")
        self.driver = User.objects.create_user("d1", password="x")

    def test_place_order_guard_blocks_unverified(self):
        with self.assertRaises(PermissionDenied):
            services.place_order_guard(self.user)

    def test_place_order_guard_allows_verified(self):
        auth_services.confirm_account(self.user)
        self.assertIsNone(services.place_order_guard(self.user))

    def test_orders_for_dispatch_excludes_assigned(self):
        free = make_order()
        make_order(driver=self.driver)
        self.assertEqual(list(services.orders_for_dispatch()), [free])

    def test_all_orders_returns_everything(self):
        make_order()
        make_order(driver=self.driver)
        self.assertEqual(services.all_orders().count(), 2)
