"""Settings shared by every environment. Secrets are read in the environment modules."""

import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# --- Multi-tenancy (increment 1.2) -------------------------------------------
# Schema-per-tenant via django-tenants. Apps in SHARED_APPS live in the public
# schema (tenant registry, auth is per-tenant); TENANT_APPS are migrated into
# every tenant schema on provisioning.
SHARED_APPS = [
    "django_tenants",
    "tenants",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
]

TENANT_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
]

INSTALLED_APPS = list(SHARED_APPS) + [a for a in TENANT_APPS if a not in SHARED_APPS]

TENANT_MODEL = "tenants.Tenant"
TENANT_DOMAIN_MODEL = "tenants.Domain"

MIDDLEWARE = [
    # Must be first: selects the tenant schema from the request hostname.
    # (Our subclass exempts /healthz so probes work on a fresh database.)
    "tenants.middleware.TenantMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# PostgreSQL only. Schema-per-tenant (increment 1.2) depends on it, so the
# engine is django-tenants' postgres backend rather than Django's default.
DATABASES = {
    "default": dj_database_url.config(
        default="postgres://cascadia:cascadia@localhost:5432/cascadia",
        conn_max_age=60,
        engine="django_tenants.postgresql_backend",
    )
}
DATABASES["default"].setdefault("OPTIONS", {})["connect_timeout"] = 5

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
