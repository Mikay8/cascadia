"""Tests for increment 1.2: tenant provisioning.

Done when: creating a tenant creates its schema and applies all migrations.
"""

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import connection
from django.test import Client, override_settings
from django_tenants.utils import get_public_schema_name, schema_context

from tenants.models import Domain, Tenant


def _schema_exists(schema_name: str) -> bool:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_namespace WHERE nspname = %s", [schema_name])
        return cursor.fetchone() is not None


def _table_exists(schema_name: str, table_name: str) -> bool:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM pg_tables WHERE schemaname = %s AND tablename = %s",
            [schema_name, table_name],
        )
        return cursor.fetchone() is not None


@pytest.mark.django_db(transaction=True)
def test_creating_tenant_provisions_schema_and_runs_migrations() -> None:
    tenant = Tenant(schema_name="acme", name="Acme Community Loan Fund")
    tenant.save()

    assert _schema_exists("acme")
    # Tenant apps are migrated into the new schema: auth tables exist there.
    assert _table_exists("acme", "auth_user")
    # ...but not duplicated into the public schema.
    assert not _table_exists(get_public_schema_name(), "auth_user")


@pytest.mark.django_db(transaction=True)
def test_tenant_data_is_isolated_between_schemas() -> None:
    for schema in ("alpha", "beta"):
        Tenant(schema_name=schema, name=schema.title()).save()

    with schema_context("alpha"):
        User.objects.create(username="alpha-user")
    with schema_context("beta"):
        User.objects.create(username="beta-user")

    with schema_context("alpha"):
        assert list(User.objects.values_list("username", flat=True)) == ["alpha-user"]
    with schema_context("beta"):
        assert list(User.objects.values_list("username", flat=True)) == ["beta-user"]


@pytest.mark.django_db(transaction=True)
def test_tenant_registry_lives_in_the_public_schema() -> None:
    Tenant(schema_name="gamma", name="Gamma Fund").save()

    with schema_context(get_public_schema_name()):
        assert Tenant.objects.filter(schema_name="gamma").exists()


@pytest.mark.django_db(transaction=True)
def test_reserved_schema_name_is_rejected() -> None:
    # django-tenants only guards the pg_* prefix (reserved by PostgreSQL)
    # and the 63-character limit.
    tenant = Tenant(schema_name="pg_shadow", name="Bad")
    with pytest.raises(ValidationError):
        tenant.full_clean()


@pytest.mark.django_db(transaction=True)
def test_unknown_hostname_returns_404(client: Client) -> None:
    with override_settings(ALLOWED_HOSTS=["testserver", "unknown.test"]):
        response = client.get("/healthz", HTTP_HOST="unknown.test")
    assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_known_tenant_domain_routes_to_its_schema(client: Client) -> None:
    tenant = Tenant(schema_name="delta", name="Delta Fund")
    tenant.save()
    Domain.objects.create(domain="delta.test", tenant=tenant, is_primary=True)

    with override_settings(ALLOWED_HOSTS=["testserver", "delta.test"]):
        response = client.get("/healthz", HTTP_HOST="delta.test")

    assert response.status_code == 200
    assert connection.schema_name == "delta"
