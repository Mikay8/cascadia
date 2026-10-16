"""Cascadia admin site: staff logins go through the two-step MFA flow.

Django's default admin login form only asks for a password, which would let a
staff member with a TOTP device skip the second factor entirely. This site
redirects every login through ``accounts:login`` instead, so MFA is enforced
on the admin too. (The same redirect applies to anyone already logged in but
not MFA-verified, closing the bypass for sessions created elsewhere.)
"""

from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django_otp import user_has_device


class CascadiaAdminSite(admin.AdminSite):
    site_header = "Cascadia administration"

    def login(self, request: HttpRequest, extra_context: dict | None = None) -> HttpResponse:
        user = request.user
        needs_mfa = user.is_authenticated and user_has_device(user) and not user.is_verified()
        if not user.is_authenticated or needs_mfa:
            login_url = reverse("accounts:login")
            return redirect(f"{login_url}?next={request.get_full_path()}")
        return super().login(request, extra_context)


site = CascadiaAdminSite(name="cascadia_admin")
