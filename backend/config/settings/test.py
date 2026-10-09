"""Test runner settings."""

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "test-only-insecure-key"  # noqa: S105
ALLOWED_HOSTS = ["testserver"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Serve static files from the apps directly; no collectstatic needed outside production.
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
