from django.contrib import admin

from .models import (
    Order, Profile,
    VehicleClass, Capability, Vertical, TransporterVehicle,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "is_business", "company", "vehicle_id", "rating", "online")
    list_filter = ("role", "is_business", "online")
    search_fields = ("user__username", "user__first_name", "company")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("code", "client", "from_name", "to_name", "vehicle_name", "status", "driver_name", "price", "created_at")
    list_filter = ("status", "service_type", "vehicle_id")
    search_fields = ("code", "from_name", "to_name", "client__username", "driver_name")


# --- Taxonomia multi-verticala --------------------------------------------

@admin.register(VehicleClass)
class VehicleClassAdmin(admin.ModelAdmin):
    list_display = ("rank", "name", "slug", "max_weight_kg", "volume_m3", "active")
    list_editable = ("active",)
    ordering = ("rank",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Capability)
class CapabilityAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "needs_document", "description")
    list_filter = ("needs_document",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Vertical)
class VerticalAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "min_vehicle_class", "active")
    list_filter = ("active",)
    filter_horizontal = ("required_capabilities",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(TransporterVehicle)
class TransporterVehicleAdmin(admin.ModelAdmin):
    list_display = ("label", "owner", "vehicle_class", "verified", "responsibility_accepted", "active", "created_at")
    list_filter = ("verified", "active", "vehicle_class", "capabilities")
    list_editable = ("verified",)
    filter_horizontal = ("capabilities",)
    search_fields = ("label", "plate", "owner__username")
