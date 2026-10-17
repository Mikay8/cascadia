"""Login, TOTP challenge, MFA enrollment, and logout (increment 1.4).

Login is two steps. Step 1 checks the password; if the user has a confirmed
TOTP device, the user id is parked in the session (the user is *not* logged
in yet) and step 2 asks for the authenticator code. MFA is per-user: it only
kicks in once the user enrolls a device. All of this runs inside the tenant
schema selected by the tenant middleware, so users, sessions, and TOTP
devices are per-tenant by construction.
"""

import base64
from base64 import b32encode
from io import BytesIO

import qrcode
from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django_otp.plugins.otp_totp.models import TOTPDevice

from .forms import TOTPTokenForm
from .services import (
    begin_login,
    clear_pending_mfa,
    complete_mfa_login,
    confirmed_devices,
    get_pending_mfa_user,
    verify_mfa_token,
)


def _safe_next_url(request: HttpRequest, default: str) -> str:
    """Return the ?next= target only if it is a safe same-host URL."""
    candidate = request.POST.get("next") or request.GET.get("next") or default
    if url_has_allowed_host_and_scheme(candidate, allowed_hosts={request.get_host()}):
        return candidate
    return default


def login_view(request: HttpRequest) -> HttpResponse:
    """Step 1: username and password."""
    redirect_to = _safe_next_url(request, settings.LOGIN_REDIRECT_URL)
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if begin_login(request, user):
                mfa_url = reverse("accounts:mfa")
                return redirect(f"{mfa_url}?next={redirect_to}")
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
    user = get_pending_mfa_user(request)
    if user is None:
        clear_pending_mfa(request)
        return redirect("accounts:login")
    redirect_to = _safe_next_url(request, settings.LOGIN_REDIRECT_URL)
    devices = confirmed_devices(user)
    if not devices:
        # MFA was disabled mid-flow; fall back to a plain login.
        complete_mfa_login(request, user, None)
        return redirect(redirect_to)
    if request.method == "POST":
        form = TOTPTokenForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data["token"]
            device = verify_mfa_token(user, token)
            if device is not None:
                complete_mfa_login(request, user, device)
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
    confirmed = confirmed_devices(user)
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
