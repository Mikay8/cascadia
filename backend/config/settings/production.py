"""Staging and production. Every secret comes from the environment and is required."""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ImproperlyConfigured(f"{name} must be set")
    return value


DEBUG = False
SECRET_KEY = _require("DJANGO_SECRET_KEY")
_require("DATABASE_URL")
if not ALLOWED_HOSTS:  # noqa: F405
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must be set")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
