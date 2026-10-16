"""Per-tenant authentication: login, TOTP MFA, and session timeouts."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
