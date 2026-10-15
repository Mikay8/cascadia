"""Shared pytest fixtures for the back-end suite."""

import pytest

from tenants.models import Domain, Tenant


@pytest.fixture(autouse=True)
def _public_tenant_with_testserver_domain(db) -> None:
    """Every hostname must map to a tenant or the middleware 404s.

    The Django test client talks to ``testserver``, so the public tenant
    owns that domain for the whole suite (creating a ``public`` tenant
    never creates a schema; it only registers the row).
    """
    tenant, _ = Tenant.objects.get_or_create(schema_name="public", defaults={"name": "Public"})
    Domain.objects.get_or_create(domain="testserver", tenant=tenant, defaults={"is_primary": True})
