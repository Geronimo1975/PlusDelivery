from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("gate/", views.gate, name="gate"),
    path("driver/apply/", views.driver_apply, name="driver_apply"),
    path("admin/", views.admin_home, name="admin_home"),
    path("admin/driver/approve/", views.approve_driver, name="approve_driver"),
]
