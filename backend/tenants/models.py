"""Tenant and domain models.

Each row in ``Tenant`` is one CDFI organization. Its ``schema_name`` is the
PostgreSQL schema that holds all of that tenant data; schemas are created
(and migrated) automatically when the tenant is saved. ``Domain`` maps a
hostname to a tenant so the middleware can route each request to the right
schema. Both tables live in the shared ``public`` schema.
"""

from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


class Tenant(TenantMixin):
    """One CDFI organization. Saving a new tenant provisions its schema."""

    name = models.CharField(max_length=200)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.schema_name})"


class Domain(DomainMixin):
    """Hostname routing to a tenant. Kept minimal; see django-tenants docs."""

    def __str__(self) -> str:
        return self.domain
