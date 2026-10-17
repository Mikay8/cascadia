"""Shared two-step login logic (increments 1.4 and 1.10).

Step 1 checks the password; if the user has a confirmed TOTP device, the user
id is parked in the session (the user is *not* logged in yet) and step 2
verifies the authenticator code. The Django template views in ``views.py``
and the JSON API in the ``api`` app both implement this flow; it lives here
so the two surfaces share it instead of duplicating it.

All of this runs inside the tenant schema selected by the tenant middleware,
so users, sessions, and TOTP devices are per-tenant by construction.
"""

import time

from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest
from django_otp import login as otp_login
from django_otp import user_has_device
from django_otp.plugins.otp_totp.models import TOTPDevice

from .middleware import SESSION_STARTED_AT_KEY

MFA_PENDING_USER_ID_KEY = "mfa_pending_user_id"


def confirmed_devices(user: AbstractBaseUser) -> list[TOTPDevice]:
    """The user's confirmed TOTP devices (unconfirmed enrollments excluded)."""
    return list(TOTPDevice.objects.filter(user=user, confirmed=True))


def begin_login(request: HttpRequest, user: AbstractBaseUser) -> bool:
    """Step 1 of login, after the password checked out.

    Returns True when a TOTP code is still required (the user id is parked
    in the session and the user is NOT authenticated yet), False when the
    user is now fully logged in.
    """
    if user_has_device(user):
        request.session[MFA_PENDING_USER_ID_KEY] = user.pk
        request.session.cycle_key()
        return True
    auth_login(request, user)
    _stamp_session_start(request)
    return False


def get_pending_mfa_user(request: HttpRequest) -> AbstractBaseUser | None:
    """The user parked by step 1, or None when there is no pending login."""
    user_id = request.session.get(MFA_PENDING_USER_ID_KEY)
    if not user_id:
        return None
    return get_user_model().objects.filter(pk=user_id, is_active=True).first()


def verify_mfa_token(user: AbstractBaseUser, token: str) -> TOTPDevice | None:
    """Return the confirmed device whose code matches, or None.

    ``verify_token`` applies django-otp's built-in throttling, so repeated
    guesses are slowed down automatically.
    """
    return next((d for d in confirmed_devices(user) if d.verify_token(token)), None)


def complete_mfa_login(
    request: HttpRequest, user: AbstractBaseUser, device: TOTPDevice | None
) -> None:
    """Step 2 of login.

    ``device`` is None when MFA was disabled mid-flow, in which case this
    falls back to a plain login (same behavior as the template view).
    """
    request.session.pop(MFA_PENDING_USER_ID_KEY, None)
    auth_login(request, user)
    if device is not None:
        otp_login(request, device)
    _stamp_session_start(request)


def clear_pending_mfa(request: HttpRequest) -> None:
    """Drop a pending step-1 without logging anyone in."""
    request.session.pop(MFA_PENDING_USER_ID_KEY, None)


def _stamp_session_start(request: HttpRequest) -> None:
    # Server-side timestamp for the absolute session timeout middleware.
    request.session[SESSION_STARTED_AT_KEY] = time.time()
