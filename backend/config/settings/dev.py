"""Local development. Seed data only; never point this at real data."""

import os

from .base import *  # noqa: F403

DEBUG = True
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-insecure-key")
ALLOWED_HOSTS = ALLOWED_HOSTS or ["localhost", "127.0.0.1"]  # noqa: F405

# Serve static files from the apps directly; no collectstatic needed outside production.
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
