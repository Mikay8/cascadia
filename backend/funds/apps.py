"""Core fund-administration tables, one set per tenant schema (increment 1.3)."""

from django.apps import AppConfig


class FundsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "funds"
