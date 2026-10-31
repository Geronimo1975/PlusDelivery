from django.urls import include, path

app_name = "dashboard"

urlpatterns = [
    path("authorization/", include("dashboard.authorization.urls")),
    path("accounts/", include("dashboard.accounts.urls")),
    path("finance/", include("dashboard.finance.urls")),
    path("logistics/", include("dashboard.logistics.urls")),
    # Radacina dashboard-ului: modulul core (expune `dashboard:home`)
    path("", include("dashboard.core.urls")),
]
