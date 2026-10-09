"""Test runner settings."""

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "test-only-insecure-key"  # noqa: S105
ALLOWED_HOSTS = ["testserver"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
