"""Tenant registry for Cascadia's schema-per-tenant multitenancy (increment 1.2)."""

from django.apps import AppConfig


class TenantsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tenants"
