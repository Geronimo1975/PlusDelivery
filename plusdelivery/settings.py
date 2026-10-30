"""
Setari Django pentru PlusDelivery.

Ruleaza imediat local cu SQLite, fara nicio variabila de mediu (valorile de mai
jos au fallback-uri de dezvoltare). In productie, TOTUL se controleaza din mediu
(vezi .env.example): SECRET_KEY real, DEBUG=0, ALLOWED_HOSTS, DATABASE_URL (Postgres).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def _env_list(name, default=""):
    return [x.strip() for x in os.environ.get(name, default).split(",") if x.strip()]


# --- Securitate de baza (din mediu in productie) ---------------------------
# INLOCUIESTE IN PRODUCTIE: DJANGO_SECRET_KEY setat ca variabila de mediu.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-plusdelivery-prototip-schimba-ma")
DEBUG = _env_bool("DJANGO_DEBUG", True)  # in productie: DJANGO_DEBUG=0
# Local (DEBUG) acceptam orice host; in productie e OBLIGATORIU ALLOWED_HOSTS.
ALLOWED_HOSTS = _env_list("ALLOWED_HOSTS") or (["*"] if DEBUG else [])
# Necesar pt. CSRF cand aplicatia e in spatele unui proxy HTTPS (ex. Nginx).
CSRF_TRUSTED_ORIGINS = _env_list("CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "daphne",  # server ASGI pentru runserver (trebuie inaintea staticfiles)
    "channels",  # WebSocket / urmarire live
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "delivery",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serveste fisierele statice in productie
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "plusdelivery.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "plusdelivery.wsgi.application"
ASGI_APPLICATION = "plusdelivery.asgi.application"

# Channel layer in memorie (fara Redis) - potrivit pentru un SINGUR proces.
# Designul realtime (realtime._loop, "ceasul" din event-loop) presupune un singur
# proces, de aceea productia ruleaza un singur worker Daphne -> InMemory e corect.
# Daca scalezi pe mai multe procese: seteaza REDIS_URL si comuta pe channels_redis
# (atunci muta si broadcasterul realtime intr-un singur worker dedicat).
if os.environ.get("REDIS_URL"):
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [os.environ["REDIS_URL"]]},
        },
    }
else:
    CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

# Baza de date: Postgres in productie (DATABASE_URL), SQLite local ca fallback.
if os.environ.get("DATABASE_URL"):
    import dj_database_url

    DATABASES = {"default": dj_database_url.config(conn_max_age=600, conn_health_checks=True)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "de"  # limba sursa / implicita (ca lalamove.eu)
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

from django.utils.translation import gettext_lazy as _  # noqa: E402

LANGUAGES = [
    ("de", _("Deutsch")),
    ("en", _("English")),
]
LOCALE_PATHS = [BASE_DIR / "locale"]

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # tinta collectstatic (servit de WhiteNoise)
# WhiteNoise: comprima + versioneaza fisierele statice pentru cache pe termen lung.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Intarire de securitate (activa doar in productie, cand DEBUG=0) --------
if not DEBUG:
    # Suntem in spatele unui proxy (Nginx) care face terminarea TLS.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = _env_bool("SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
