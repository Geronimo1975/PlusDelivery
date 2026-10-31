from django.contrib import admin
from django.utils import timezone

from .models import AccountVerification, DriverApplication


@admin.register(AccountVerification)
class AccountVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "is_verified", "verified_via", "verified_at")
    list_filter = ("is_verified", "verified_via")
    search_fields = ("user__username", "user__email")


@admin.register(DriverApplication)
class DriverApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "submitted_at", "reviewed_by", "reviewed_at")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email")
    actions = ["approve_selected", "reject_selected"]

    @admin.action(description="Aprobă (verifică și vehiculele)")
    def approve_selected(self, request, queryset):
        # Setarea status=approved declanseaza semnalul din delivery care
        # verifica vehiculele soferului.
        n = 0
        for app in queryset:
            app.status = DriverApplication.Status.APPROVED
            app.reviewed_by = request.user
            app.reviewed_at = timezone.now()
            app.save(update_fields=["status", "reviewed_by", "reviewed_at"])
            n += 1
        self.message_user(request, f"{n} aplicație(i) aprobată(e); vehiculele au fost verificate.")

    @admin.action(description="Respinge")
    def reject_selected(self, request, queryset):
        for app in queryset:
            app.status = DriverApplication.Status.REJECTED
            app.reviewed_by = request.user
            app.reviewed_at = timezone.now()
            app.save(update_fields=["status", "reviewed_by", "reviewed_at"])
