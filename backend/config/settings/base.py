"""Settings shared by every environment. Secrets are read in the environment modules."""

import os
from pathlib import Path

import dj_database_url
from corsheaders.defaults import default_headers

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
    # CORS headers for the demo UI's cross-origin API calls (increment 1.10).
    "corsheaders",
]

TENANT_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    # TOTP devices belong to per-tenant users, so the device tables live in
    # each tenant schema alongside auth_user (increment 1.4).
    "django_otp.plugins.otp_totp",
    # Login / MFA views serve per-tenant users (no models of its own).
    "accounts",
    # JSON API for the demo UI (increment 1.10). No models of its own; its
    # views must run inside the tenant schema like the template views.
    "api",
    "funds",
]

INSTALLED_APPS = list(SHARED_APPS) + [a for a in TENANT_APPS if a not in SHARED_APPS]

TENANT_MODEL = "tenants.Tenant"
TENANT_DOMAIN_MODEL = "tenants.Domain"

MIDDLEWARE = [
    # Must be first: selects the tenant schema from the request hostname.
    # (Our subclass exempts /healthz so probes work on a fresh database.)
    "tenants.middleware.TenantMiddleware",
    # CORS as high as possible, right after tenant selection, so preflights
    # get their headers even when a later middleware returns early.
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Annotates request.user with is_verified(); must follow auth middleware.
    "django_otp.middleware.OTPMiddleware",
    # Enforces the absolute session timeout after login (increment 1.4).
    "accounts.middleware.AbsoluteSessionTimeoutMiddleware",
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

# --- Authentication and sessions (increment 1.4) ------------------------------
# Sessions are short on purpose: 30 minutes of idle time ends the session
# (SESSION_SAVE_EVERY_REQUEST refreshes the cookie and the server-side expiry
# on every request, so activity keeps it alive), and the absolute timeout
# middleware below caps a session at 30 minutes from login no matter what.
# Both are enforced server-side in the session store, not just the cookie.
SESSION_COOKIE_AGE = 30 * 60
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
# SESSION_COOKIE_SECURE is set in production.py (dev serves over plain HTTP).
CASCADIA_ABSOLUTE_SESSION_TIMEOUT = 30 * 60  # seconds from login

# Issuer label shown in authenticator apps when enrolling TOTP.
OTP_TOTP_ISSUER = "Cascadia"

# --- Demo UI cross-origin API access (increment 1.10) -------------------------
# The React frontend is a different origin from the backend in UAT. The API
# allows it only when named here (comma-separated). Credentials (session
# cookie) are allowed; CSRF still enforced per request.
CORS_ALLOWED_ORIGINS = [o for o in os.environ.get("CASCADIA_CORS_ORIGINS", "").split(",") if o]
CORS_ALLOW_CREDENTIALS = True
# The demo UI sends X-Tenant on every API request; it must be allow-listed
# for preflight or the browser blocks the actual request after OPTIONS.
CORS_ALLOW_HEADERS = (*default_headers, "x-tenant")

# Cross-origin session auth (increment 1.10.2): when CORS origins are
# configured, the SPA runs on a different origin and the browser withholds
# SameSite=Lax cookies on cross-origin requests. That breaks session auth
# (no session cookie sent) and CSRF validation (no CSRF cookie sent to
# compare the X-CSRFToken header against). SameSite=None allows them;
# Secure is already True in production.py (dev stays on Lax over HTTP).
if CORS_ALLOWED_ORIGINS:
    SESSION_COOKIE_SAMESITE = "None"
    CSRF_COOKIE_SAMESITE = "None"

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/accounts/login/"
