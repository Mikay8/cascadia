"""Staging and production. Every secret comes from the environment and is required.

Nothing here is specific to one host. The same settings run on Railway or AWS; only the
environment variables differ (see docs/INFRASTRUCTURE.md).
"""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ImproperlyConfigured(f"{name} must be set")
    return value


def _list(name: str) -> list[str]:
    return [item for item in os.environ.get(name, "").split(",") if item]


DEBUG = False
SECRET_KEY = _require("DJANGO_SECRET_KEY")
_require("DATABASE_URL")
if not ALLOWED_HOSTS:  # noqa: F405
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must be set")

CSRF_TRUSTED_ORIGINS = _list("DJANGO_CSRF_TRUSTED_ORIGINS")

# TLS ends at the platform's load balancer, which forwards the original scheme.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
# Platform health checks call /healthz over plain HTTP inside the private network.
SECURE_REDIRECT_EXEMPT = [r"^healthz$"]
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
