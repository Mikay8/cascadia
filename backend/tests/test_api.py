"""Tests for increment 1.10: the demo JSON API.

Covers the CSRF flow, the two-step JSON login (with and without a TOTP
device), tenant selection via the X-Tenant header (including isolation),
money serialized as strings, and seed_demo idempotency with PRIMARY_DOMAIN.
"""

import json
import os
from unittest import mock

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection
from django.test import Client
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_tenants.utils import get_public_schema_name, schema_context

from tenants.models import Domain, Tenant

PASSWORD = "s3cret-pass"
SCHEMAS = ("acme", "harbor", "mesa")


@pytest.fixture(autouse=True)
def _isolate_tenant_data():
    """Wipe tenant schemas between tests (pytest-django only flushes the
    connection's current schema)."""
    yield
    for schema in SCHEMAS:
        with schema_context(schema):
            call_command("flush", interactive=False, verbosity=0)
    with schema_context(get_public_schema_name()):
        Tenant.objects.all().delete()
    connection.set_schema_to_public()


def _seed() -> None:
    with schema_context(get_public_schema_name()):
        call_command("seed_demo", verbosity=0)


def _post(client: Client, path: str, payload: dict, schema: str = "acme") -> object:
    return client.post(
        path,
        data=json.dumps(payload),
        content_type="application/json",
        HTTP_X_TENANT=schema,
    )


def _get(client: Client, path: str, schema: str = "acme") -> object:
    return client.get(path, HTTP_X_TENANT=schema)


def _confirm_device(username: str, schema: str = "acme") -> TOTPDevice:
    with schema_context(schema):
        user = User.objects.get(username=username)
        device = TOTPDevice.objects.create(user=user, name="test", confirmed=False)
        device.confirmed = True
        device.save()
        return device


def _current_token(device: TOTPDevice) -> str:
    return str(totp(device.bin_key)).zfill(6)


def _login_demo(client: Client, schema: str = "acme") -> None:
    resp = _post(client, "/api/auth/login/", {"username": "demo", "password": "demo-pass"}, schema)
    assert resp.status_code == 200, resp.content[:200]
    assert resp.json() == {"mfa_required": False}


@pytest.mark.django_db(transaction=True)
def test_csrf_endpoint_sets_cookie(client: Client) -> None:
    _seed()
    resp = client.get("/api/auth/csrf/", HTTP_X_TENANT="acme")
    assert resp.status_code == 200
    assert resp.json() == {"detail": "ok"}
    assert "csrftoken" in resp.cookies


@pytest.mark.django_db(transaction=True)
def test_post_requires_csrf_token() -> None:
    _seed()
    client = Client(enforce_csrf_checks=True)
    # No CSRF token -> 403, even with valid credentials.
    resp = client.post(
        "/api/auth/login/",
        data=json.dumps({"username": "demo", "password": "demo-pass"}),
        content_type="application/json",
        HTTP_X_TENANT="acme",
    )
    assert resp.status_code == 403
    # With the token from /api/auth/csrf/ -> not 403 (400 would be bad creds).
    client.get("/api/auth/csrf/", HTTP_X_TENANT="acme")
    token = client.cookies["csrftoken"].value
    resp = client.post(
        "/api/auth/login/",
        data=json.dumps({"username": "demo", "password": "wrong"}),
        content_type="application/json",
        HTTP_X_TENANT="acme",
        HTTP_X_CSRFTOKEN=token,
    )
    assert resp.status_code == 400  # invalid credentials, not CSRF failure


@pytest.mark.django_db(transaction=True)
def test_login_without_mfa_device_logs_in(client: Client) -> None:
    _seed()
    resp = _post(client, "/api/auth/login/", {"username": "demo", "password": "demo-pass"})
    assert resp.status_code == 200
    assert resp.json() == {"mfa_required": False}
    me = _get(client, "/api/auth/me/")
    assert me.status_code == 200
    assert me.json() == {"username": "demo"}


@pytest.mark.django_db(transaction=True)
def test_login_bad_credentials_rejected(client: Client) -> None:
    _seed()
    resp = _post(client, "/api/auth/login/", {"username": "demo", "password": "nope"})
    assert resp.status_code == 400
    assert _get(client, "/api/auth/me/").status_code == 403


@pytest.mark.django_db(transaction=True)
def test_login_with_mfa_device_requires_token(client: Client) -> None:
    _seed()
    device = _confirm_device("demo")
    resp = _post(client, "/api/auth/login/", {"username": "demo", "password": "demo-pass"})
    assert resp.status_code == 200
    assert resp.json() == {"mfa_required": True}
    # Parked, not logged in yet.
    assert _get(client, "/api/auth/me/").status_code == 403
    # Wrong code -> 400, still parked.
    bad = _post(client, "/api/auth/mfa/", {"token": "000000"})
    assert bad.status_code == 400
    assert _get(client, "/api/auth/me/").status_code == 403
    # django-otp throttles after a failed attempt; reset for the good one.
    device.throttle_reset()
    # Right code -> logged in.
    good = _post(client, "/api/auth/mfa/", {"token": _current_token(device)})
    assert good.status_code == 200
    me = _get(client, "/api/auth/me/")
    assert me.status_code == 200
    assert me.json() == {"username": "demo"}


@pytest.mark.django_db(transaction=True)
def test_mfa_without_pending_login_rejected(client: Client) -> None:
    _seed()
    resp = _post(client, "/api/auth/mfa/", {"token": "123456"})
    assert resp.status_code == 400


@pytest.mark.django_db(transaction=True)
def test_logout_ends_session(client: Client) -> None:
    _seed()
    _login_demo(client)
    assert _get(client, "/api/auth/me/").status_code == 200
    resp = _post(client, "/api/auth/logout/", {})
    assert resp.status_code == 200
    assert _get(client, "/api/auth/me/").status_code == 403


@pytest.mark.django_db(transaction=True)
def test_funds_requires_auth(client: Client) -> None:
    _seed()
    assert _get(client, "/api/funds/").status_code == 403
    assert client.get("/api/funds/1/").status_code == 403


@pytest.mark.django_db(transaction=True)
def test_funds_list_and_detail(client: Client) -> None:
    _seed()
    _login_demo(client)
    resp = _get(client, "/api/funds/")
    assert resp.status_code == 200
    funds = resp.json()
    assert [f["name"] for f in funds] == ["Acme Revolving Loan Fund"]
    fund_id = funds[0]["id"]

    detail = _get(client, f"/api/funds/{fund_id}/")
    assert detail.status_code == 200
    body = detail.json()
    # Classes come out in rank (payout) order.
    assert [c["name"] for c in body["share_classes"]] == ["Class A", "Class B", "Class C"]
    assert [c["rank"] for c in body["share_classes"]] == [1, 2, 3]
    # Hard rule 1: money travels as strings, never floats.
    for cls in body["share_classes"]:
        for commitment in cls["commitments"]:
            assert isinstance(commitment["amount"], str)
    for loan in body["loans"]:
        assert isinstance(loan["principal"], str)
        assert isinstance(loan["outstanding_balance"], str)
    assert any(c["amount"] == "5000000.00" for c in body["share_classes"][0]["commitments"])
    assert _get(client, "/api/funds/999999/").status_code == 404


@pytest.mark.django_db(transaction=True)
def test_tenant_isolation_via_header() -> None:
    _seed()
    # Sessions are per-tenant (session rows live in the tenant schema), so a
    # login under one tenant does not carry over to another: log in per tenant.
    acme_client, harbor_client = Client(), Client()
    _login_demo(acme_client, "acme")
    _login_demo(harbor_client, "harbor")
    acme_funds = _get(acme_client, "/api/funds/", "acme").json()
    harbor_funds = _get(harbor_client, "/api/funds/", "harbor").json()
    assert [f["name"] for f in acme_funds] == ["Acme Revolving Loan Fund"]
    assert [f["name"] for f in harbor_funds] == ["Harbor Small Business Fund"]
    # Ids are per-tenant (each schema has its own sequence), so the same id
    # under the harbor header resolves to the HARBOR fund, never acme's.
    detail = _get(harbor_client, f"/api/funds/{acme_funds[0]['id']}/", "harbor")
    assert detail.status_code == 200
    assert detail.json()["name"] == "Harbor Small Business Fund"
    # ...and the acme session is useless under the harbor header.
    assert _get(acme_client, "/api/funds/", "harbor").status_code == 403


@pytest.mark.django_db(transaction=True)
def test_unknown_tenant_header_404s(client: Client) -> None:
    _seed()
    assert _get(client, "/api/funds/", "nope").status_code == 404
    # Schema-name injection cannot escape to arbitrary schemas.
    assert _get(client, "/api/funds/", "information_schema").status_code == 404


@pytest.mark.django_db(transaction=True)
def test_seed_demo_idempotent_with_primary_domain() -> None:
    with mock.patch.dict(os.environ, {"PRIMARY_DOMAIN": "backend-uat.example.com"}):
        with schema_context(get_public_schema_name()):
            call_command("seed_demo", verbosity=0)
            call_command("seed_demo", verbosity=0)
            domains = list(
                Domain.objects.filter(domain="backend-uat.example.com").values_list(
                    "tenant__schema_name", flat=True
                )
            )
            assert domains == ["acme"]
            # The localhost domains are kept too.
            assert Domain.objects.filter(domain="acme.localhost").exists()
        for schema in SCHEMAS:
            with schema_context(schema):
                user = User.objects.get(username="demo")
                assert user.check_password("demo-pass")
                assert user.is_staff and user.is_superuser
