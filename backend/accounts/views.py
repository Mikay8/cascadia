"""Login, TOTP challenge, MFA enrollment, and logout (increment 1.4).

Login is two steps. Step 1 checks the password; if the user has a confirmed
TOTP device, the user id is parked in the session (the user is *not* logged
in yet) and step 2 asks for the authenticator code. MFA is per-user: it only
kicks in once the user enrolls a device. All of this runs inside the tenant
schema selected by the tenant middleware, so users, sessions, and TOTP
devices are per-tenant by construction.
"""

import base64
import time
from base64 import b32encode
from io import BytesIO

import qrcode
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django_otp import login as otp_login
from django_otp import user_has_device
from django_otp.plugins.otp_totp.models import TOTPDevice

from .forms import TOTPTokenForm
from .middleware import SESSION_STARTED_AT_KEY

MFA_PENDING_USER_ID_KEY = "mfa_pending_user_id"


def _safe_next_url(request: HttpRequest, default: str) -> str:
    """Return the ?next= target only if it is a safe same-host URL."""
    candidate = request.POST.get("next") or request.GET.get("next") or default
    if url_has_allowed_host_and_scheme(candidate, allowed_hosts={request.get_host()}):
        return candidate
    return default


def _confirmed_devices(user: AbstractBaseUser) -> list[TOTPDevice]:
    return list(TOTPDevice.objects.filter(user=user, confirmed=True))


def login_view(request: HttpRequest) -> HttpResponse:
    """Step 1: username and password."""
    redirect_to = _safe_next_url(request, settings.LOGIN_REDIRECT_URL)
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user_has_device(user):
                # Park the user id; they are NOT authenticated until step 2.
                request.session[MFA_PENDING_USER_ID_KEY] = user.pk
                request.session.cycle_key()
                mfa_url = reverse("accounts:mfa")
                return redirect(f"{mfa_url}?next={redirect_to}")
            auth_login(request, user)
            return redirect(redirect_to)
    else:
        form = AuthenticationForm(request)
    return render(
        request,
        "accounts/login.html",
        {"form": form, "next": request.GET.get("next", "")},
    )


def mfa_view(request: HttpRequest) -> HttpResponse:
    """Step 2: TOTP code. Requires a pending user id from step 1."""
    user_id = request.session.get(MFA_PENDING_USER_ID_KEY)
    user = get_user_model().objects.filter(pk=user_id, is_active=True).first() if user_id else None
    if user is None:
        request.session.pop(MFA_PENDING_USER_ID_KEY, None)
        return redirect("accounts:login")
    redirect_to = _safe_next_url(request, settings.LOGIN_REDIRECT_URL)
    devices = _confirmed_devices(user)
    if not devices:
        # MFA was disabled mid-flow; fall back to a plain login.
        request.session.pop(MFA_PENDING_USER_ID_KEY, None)
        auth_login(request, user)
        return redirect(redirect_to)
    if request.method == "POST":
        form = TOTPTokenForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data["token"]
            # verify_token applies django-otp's built-in throttling, so
            # repeated guesses are slowed down automatically.
            device = next((d for d in devices if d.verify_token(token)), None)
            if device is not None:
                request.session.pop(MFA_PENDING_USER_ID_KEY, None)
                auth_login(request, user)
                otp_login(request, device)
                request.session[SESSION_STARTED_AT_KEY] = time.time()
                return redirect(redirect_to)
            form.add_error("token", "That code did not match. Try the current code.")
    else:
        form = TOTPTokenForm()
    return render(request, "accounts/mfa.html", {"form": form, "next": request.GET.get("next", "")})


def _device_qr_data_uri(device: TOTPDevice) -> str:
    img = qrcode.make(device.config_url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


@login_required
def mfa_setup_view(request: HttpRequest) -> HttpResponse:
    """Enroll (or disable) TOTP MFA for the logged-in user."""
    user = request.user
    confirmed = _confirmed_devices(user)
    pending_device: TOTPDevice | None = None
    if not confirmed:
        pending_device, _ = TOTPDevice.objects.get_or_create(
            user=user, confirmed=False, defaults={"name": "Authenticator app"}
        )
    if request.method == "POST":
        action = request.POST.get("action")
        form = TOTPTokenForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data["token"]
            if action == "confirm" and pending_device is not None:
                if pending_device.verify_token(token):
                    pending_device.confirmed = True
                    pending_device.save()
                    return redirect("accounts:mfa_setup")
                form.add_error("token", "That code did not match. Try the current code.")
            elif action == "disable" and confirmed:
                device = next((d for d in confirmed if d.verify_token(token)), None)
                if device is not None:
                    device.delete()
                    return redirect("accounts:mfa_setup")
                form.add_error("token", "That code did not match. Try the current code.")
    else:
        form = TOTPTokenForm()
    context = {
        "form": form,
        "mfa_enabled": bool(confirmed),
        "qr_data_uri": _device_qr_data_uri(pending_device) if pending_device else "",
        "secret": b32encode(pending_device.bin_key).decode("ascii") if pending_device else "",
    }
    return render(request, "accounts/mfa_setup.html", context)


def logout_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        auth_logout(request)
        return redirect(settings.LOGOUT_REDIRECT_URL)
    return redirect("accounts:login")
