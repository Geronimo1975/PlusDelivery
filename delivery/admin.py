from django.contrib import admin

from .models import Order, Profile


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
