"""Tests for increment 1.4: authentication with TOTP MFA and short sessions.

Done when: login with MFA works per-tenant, with short server-side sessions.
"""

import time

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection
from django.test import Client, override_settings
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_tenants.utils import get_public_schema_name, schema_context

from tenants.models import Domain, Tenant

HOSTS = ["testserver", "acme.test", "beta.test"]
PASSWORD = "correct-horse-battery-staple-1.4"


@pytest.fixture(autouse=True)
def _isolate_tenant_data():
    """pytest-django's teardown flush only covers the connection's current
    schema, so tenant-schema rows (users, devices, sessions) would leak
    between tests. Wipe the tenant schemas here, then park the connection on
    public for its own flush."""
    yield
    for schema in ("acme", "beta"):
        with schema_context(schema):
            call_command("flush", interactive=False, verbosity=0)
    connection.set_schema_to_public()


def _make_tenants() -> None:
    # Tenant provisioning must run from the public schema; earlier tests may
    # leave the connection on a tenant schema.
    with schema_context(get_public_schema_name()):
        for schema, domain in (("acme", "acme.test"), ("beta", "beta.test")):
            tenant = Tenant(schema_name=schema, name=f"{schema.title()} Fund")
            tenant.save()
            Domain.objects.create(domain=domain, tenant=tenant, is_primary=True)


def _make_user(username: str, schema: str = "acme", **kwargs) -> User:
    with schema_context(schema):
        return User.objects.create_user(username=username, password=PASSWORD, **kwargs)


def _current_token(device: TOTPDevice) -> str:
    return str(totp(device.bin_key)).zfill(6)


def _other_token(token: str) -> str:
    return "000001" if token != "000001" else "000002"


def _login(client: Client, username: str, host: str = "acme.test"):
    return client.post(
        "/accounts/login/",
        {"username": username, "password": PASSWORD},
        HTTP_HOST=host,
    )


def _confirm_device(username: str, schema: str = "acme") -> TOTPDevice:
    """Enroll + confirm a TOTP device for the user, bypassing the views."""
    with schema_context(schema):
        user = User.objects.get(username=username)
        device = TOTPDevice.objects.create(user=user, name="test", confirmed=False)
        device.confirmed = True
        device.save()
        return device


@pytest.mark.django_db(transaction=True)
@override_settings(ALLOWED_HOSTS=HOSTS)
def test_login_without_mfa_succeeds(client: Client) -> None:
    _make_tenants()
    _make_user("alice")
    response = _login(client, "alice")
    assert response.status_code == 302
    assert "_auth_user_id" in client.session
    # Session cookie carries the 30-minute idle expiry.
    assert int(response.cookies["sessionid"]["max-age"]) == 30 * 60


@pytest.mark.django_db(transaction=True)
@override_settings(ALLOWED_HOSTS=HOSTS)
def test_totp_enrollment_flow(client: Client) -> None:
    _make_tenants()
    _make_user("alice")
    _login(client, "alice")

    response = client.get("/accounts/mfa/setup/", HTTP_HOST="acme.test")
    assert response.status_code == 200
    with schema_context("acme"):
        device = TOTPDevice.objects.get(user__username="alice")
        assert not device.confirmed
        token = _current_token(device)

    # A wrong code does not confirm the device.
    response = client.post(
        "/accounts/mfa/setup/",
        {"action": "confirm", "token": _other_token(token)},
        HTTP_HOST="acme.test",
    )
    assert response.status_code == 200
    with schema_context("acme"):
        device.refresh_from_db()
        assert not device.confirmed
        device.throttle_reset()

    # The right code confirms it.
    response = client.post(
        "/accounts/mfa/setup/", {"action": "confirm", "token": token}, HTTP_HOST="acme.test"
    )
    assert response.status_code == 302
    with schema_context("acme"):
        device.refresh_from_db()
        assert device.confirmed


@pytest.mark.django_db(transaction=True)
@override_settings(ALLOWED_HOSTS=HOSTS)
def test_login_requires_totp_once_mfa_enabled(client: Client) -> None:
    _make_tenants()
    _make_user("alice")
    with schema_context("acme"):
        device = _confirm_device("alice")
        token = _current_token(device)

    # Step 1 (password) parks the user id but does NOT authenticate.
    response = _login(client, "alice")
    assert response.status_code == 302
    assert response["Location"].startswith("/accounts/mfa/")
    assert "_auth_user_id" not in client.session
    assert client.session["mfa_pending_user_id"] is not None

    # A protected page still sees an anonymous user.
    response = client.get("/accounts/mfa/setup/", HTTP_HOST="acme.test")
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]

    # A wrong code does not authenticate.
    response = client.post("/accounts/mfa/", {"token": _other_token(token)}, HTTP_HOST="acme.test")
    assert response.status_code == 200
    assert "_auth_user_id" not in client.session
    with schema_context("acme"):
        device.refresh_from_db()
        device.throttle_reset()

    # The right code completes the login and marks the session MFA-verified.
    response = client.post("/accounts/mfa/", {"token": token}, HTTP_HOST="acme.test")
    assert response.status_code == 302
    assert "_auth_user_id" in client.session
    assert "mfa_pending_user_id" not in client.session
    assert client.session["otp_device_id"] is not None

    response = client.get("/accounts/mfa/setup/", HTTP_HOST="acme.test")
    assert response.status_code == 200
    assert b"enabled" in response.content


@pytest.mark.django_db(transaction=True)
@override_settings(ALLOWED_HOSTS=HOSTS)
def test_mfa_page_without_pending_state_redirects_to_login(client: Client) -> None:
    _make_tenants()
    response = client.get("/accounts/mfa/", HTTP_HOST="acme.test")
    assert response.status_code == 302
    assert response["Location"] == "/accounts/login/"


@pytest.mark.django_db(transaction=True)
@override_settings(ALLOWED_HOSTS=HOSTS)
def test_mfa_disable_flow(client: Client) -> None:
    _make_tenants()
    _make_user("alice")
    with schema_context("acme"):
        device = _confirm_device("alice")
        token = _current_token(device)
        # Authenticate without consuming the device's current code, so the
        # disable step below exercises a fresh (replayable) token. The session
        # row must land in the tenant's schema.
        user = User.objects.get(username="alice")
        client.force_login(user, backend="django.contrib.auth.backends.ModelBackend")

    # Disabling requires a current code from the device being removed.
    response = client.post(
        "/accounts/mfa/setup/",
        {"action": "disable", "token": _other_token(token)},
        HTTP_HOST="acme.test",
    )
    assert response.status_code == 200
    with schema_context("acme"):
        assert TOTPDevice.objects.filter(user__username="alice").exists()
        device.refresh_from_db()
        device.throttle_reset()
        token = _current_token(device)

    response = client.post(
        "/accounts/mfa/setup/", {"action": "disable", "token": token}, HTTP_HOST="acme.test"
    )
    assert response.status_code == 302
    with schema_context("acme"):
        assert not TOTPDevice.objects.filter(user__username="alice").exists()

    # With no device left, password-only login works again.
    client.post("/accounts/logout/", HTTP_HOST="acme.test")
    response = _login(client, "alice")
    assert "_auth_user_id" in client.session


@pytest.mark.django_db(transaction=True)
@override_settings(ALLOWED_HOSTS=HOSTS)
def test_absolute_session_timeout_logs_out(client: Client) -> None:
    _make_tenants()
    _make_user("alice")
    _login(client, "alice")
    assert "_auth_user_id" in client.session

    # Age the session past the absolute timeout.
    session = client.session
    session["_cascadia_session_started_at"] = time.time() - 4000
    session.save()

    with override_settings(CASCADIA_ABSOLUTE_SESSION_TIMEOUT=30 * 60):
        response = client.get("/accounts/mfa/setup/", HTTP_HOST="acme.test")
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db(transaction=True)
@override_settings(ALLOWED_HOSTS=HOSTS)
def test_session_survives_within_absolute_timeout(client: Client) -> None:
    _make_tenants()
    _make_user("alice")
    _login(client, "alice")
    with override_settings(CASCADIA_ABSOLUTE_SESSION_TIMEOUT=8 * 60 * 60):
        response = client.get("/accounts/mfa/setup/", HTTP_HOST="acme.test")
    assert response.status_code == 200
    assert "_auth_user_id" in client.session


@pytest.mark.django_db(transaction=True)
@override_settings(ALLOWED_HOSTS=HOSTS)
def test_auth_does_not_leak_across_tenants(client: Client) -> None:
    _make_tenants()
    _make_user("alice", schema="acme")

    # The user exists only in acme: login fails on beta's hostname.
    response = _login(client, "alice", host="beta.test")
    assert response.status_code == 200  # login form re-rendered, not a redirect
    assert "_auth_user_id" not in client.session

    # Login works on acme's hostname...
    response = _login(client, "alice", host="acme.test")
    assert "_auth_user_id" in client.session

    # ...but the same session cookie authenticates nobody on beta's hostname:
    # sessions live in the tenant schema, so beta has no such session.
    response = client.get("/accounts/mfa/setup/", HTTP_HOST="beta.test")
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


@pytest.mark.django_db(transaction=True)
@override_settings(ALLOWED_HOSTS=HOSTS)
def test_totp_devices_are_per_tenant(client: Client) -> None:
    _make_tenants()
    _make_user("alice", schema="acme")
    _make_user("alice", schema="beta")
    with schema_context("acme"):
        _confirm_device("alice", schema="acme")

    # Enrolled in acme: password step on acme's host demands the TOTP code.
    response = _login(client, "alice", host="acme.test")
    assert response["Location"].startswith("/accounts/mfa/")

    # Same username on beta never enrolled: password-only login succeeds.
    client2 = Client()
    response = client2.post(
        "/accounts/login/",
        {"username": "alice", "password": PASSWORD},
        HTTP_HOST="beta.test",
    )
    assert response.status_code == 302
    assert "_auth_user_id" in client2.session
    assert "mfa_pending_user_id" not in client2.session


@pytest.mark.django_db(transaction=True)
@override_settings(ALLOWED_HOSTS=HOSTS)
def test_admin_login_goes_through_mfa_flow(client: Client) -> None:
    _make_tenants()
    # Anonymous: /admin/login/ redirects into the two-step flow.
    response = client.get("/admin/login/", HTTP_HOST="acme.test")
    assert response.status_code == 302
    assert response["Location"].startswith("/accounts/login/")

    # Staff with MFA: completing the flow lands on the admin.
    _make_user("boss", schema="acme", is_staff=True)
    with schema_context("acme"):
        device = _confirm_device("boss", schema="acme")
        token = _current_token(device)
    response = client.post(
        "/accounts/login/",
        {"username": "boss", "password": PASSWORD, "next": "/admin/"},
        HTTP_HOST="acme.test",
    )
    assert response["Location"].startswith("/accounts/mfa/")
    response = client.post(
        "/accounts/mfa/", {"token": token, "next": "/admin/"}, HTTP_HOST="acme.test"
    )
    assert response["Location"] == "/admin/"
    response = client.get("/admin/", HTTP_HOST="acme.test")
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
@override_settings(ALLOWED_HOSTS=HOSTS)
def test_admin_login_cannot_bypass_mfa(client: Client) -> None:
    """A session authenticated without the TOTP step is sent back to it."""
    _make_tenants()
    _make_user("boss", schema="acme", is_staff=True)
    _confirm_device("boss", schema="acme")
    with schema_context("acme"):
        # The session row must land in the tenant's schema, so force_login
        # runs inside the schema context.
        user = User.objects.get(username="boss")
        client.force_login(user, backend="django.contrib.auth.backends.ModelBackend")
    # force_login skips our views entirely: no TOTP step happened.
    response = client.get("/admin/login/", HTTP_HOST="acme.test")
    assert response.status_code == 302
    assert response["Location"].startswith("/accounts/login/")
