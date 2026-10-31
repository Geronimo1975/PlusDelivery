from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

from delivery.urls import marketing_patterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),  # set_language (comutator limba)
    path("dashboard/", include("dashboard.urls")),
    # App functionala + API (neprefixate pe limba)
    path("", include("delivery.urls")),
]

# Site public pe limba: /de/... si /en/... ; `/` -> redirect la limba implicita.
urlpatterns += i18n_patterns(
    *marketing_patterns,
    prefix_default_language=True,
)
