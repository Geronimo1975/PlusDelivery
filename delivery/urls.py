from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views
from . import auth_api
from . import pages

# --- Site public (marketing) — se prefixeaza pe limba (/de/..., /en/...) ---
# in urlconf-ul radacina prin i18n_patterns. Structura oglinda dupa sitemap-ul
# lalamove.eu (de + en). Rutele sunt traductibile: textul sursa (germana) este
# slug-ul DE, iar traducerea EN vine din locale/en (ex. "preise" -> "pricing").
marketing_patterns = [
    path("", pages.home, name="home"),
    path(_("privatkunden"), pages.persoane, name="persoane"),
    path(_("business"), pages.business, name="business"),
    path(_("business/danke"), pages.business_thanks, name="business_thanks"),
    path(_("fahrer"), pages.curieri, name="curieri"),
    path(_("karriere"), pages.cariere, name="cariere"),

    # Servicii (hub + sub-pagini)
    path(_("services"), pages.servicii, name="servicii"),
    path(_("services/taegliche-lieferungen"), pages.serv_zilnice, name="serv_zilnice"),
    path(_("services/eillieferungen"), pages.serv_urgente, name="serv_urgente"),
    path(_("services/umzug-moebel"), pages.serv_mutari, name="serv_mutari"),
    path(_("ecommerce-integrationen"), pages.integrari, name="integrari"),
    path(_("abholorte"), pages.puncte, name="puncte"),
    path(_("preise"), pages.preturi, name="preturi"),

    # Suport & info
    path(_("faq"), pages.faq, name="faq"),
    path(_("kontakt"), pages.contact, name="contact"),
    path(_("ueber-uns"), pages.despre, name="despre"),
    path(_("sitemap"), pages.sitemap_page, name="sitemap_page"),

    # Blog
    path(_("blog"), pages.blog, name="blog"),
    path(_("blog/<slug:slug>"), pages.blog_post, name="blog_post"),

    # Legal
    path(_("agb"), pages.termeni, name="termeni"),
    path(_("datenschutz"), pages.confidentialitate, name="confidentialitate"),
    path(_("cookies"), pages.cookies, name="cookies"),
    path(_("impressum"), pages.date_firma, name="date_firma"),
]

# --- Rute neprefixate: aplicatia functionala + API -------------------------
urlpatterns = [
    # Aplicatia (SPA: client / curier / business)
    path("app", views.index, name="app"),

    # Autentificare
    path("api/auth/me", auth_api.me),
    path("api/auth/register", auth_api.register),
    path("api/auth/login", auth_api.login_view),
    path("api/auth/logout", auth_api.logout_view),

    # Date de referinta + geocodare + pret
    path("api/config", views.config),
    path("api/geocode", views.geocode),
    path("api/quote", views.quote),

    # Comenzi (client)
    path("api/orders", views.orders),
    path("api/orders/<str:code>", views.order_detail),

    # Sofer
    path("api/driver/jobs", views.driver_jobs),
    path("api/driver/online", views.driver_online),
    path("api/orders/<str:code>/accept", views.accept_order),
    path("api/orders/<str:code>/status", views.advance_status),
    path("api/orders/<str:code>/rate", views.rate_order),

    # Business (client)
    path("api/stats", views.stats),
]
