"""JSON API for the demo UI (increment 1.10).

Same two-step login as the template views (see ``accounts.services``), over
JSON: step 1 checks the password and reports whether a TOTP code is still
required; step 2 verifies the code. All state-changing endpoints are
CSRF-protected (no csrf_exempt anywhere); the SPA fetches a CSRF cookie from
``/api/auth/csrf/`` first and sends it back as ``X-CSRFToken``.

Money is serialized as strings (hard rule 1); the front end never does money
math. Every view runs inside the tenant schema selected by the tenant
middleware, so tenants never mix.
"""

import json
from typing import Any

from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.http import HttpRequest, JsonResponse
from django.middleware.csrf import get_token

from accounts.services import (
    begin_login,
    complete_mfa_login,
    confirmed_devices,
    get_pending_mfa_user,
    verify_mfa_token,
)
from funds.models import Fund


def _json_body(request: HttpRequest) -> dict[str, Any] | None:
    """Parse the request body as JSON, or return None when it is not JSON."""
    try:
        data = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _method_not_allowed(request: HttpRequest, allowed: str) -> JsonResponse | None:
    if request.method != allowed:
        return JsonResponse({"detail": "Method not allowed."}, status=405)
    return None


def _unauthenticated(request: HttpRequest) -> JsonResponse | None:
    # Session auth, but JSON-style 403 instead of a login redirect.
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=403)
    return None


def csrf_view(request: HttpRequest) -> JsonResponse:
    """Return the CSRF token in JSON so the SPA can send it back.

    The SPA runs on a different origin from the API, so it cannot read the
    CSRF cookie via document.cookie; the token comes from this response body
    instead. get_token() still sets the cookie, which Django's CSRF
    validation requires alongside the X-CSRFToken header. Safe to call often.
    """
    return JsonResponse({"detail": "ok", "csrf_token": get_token(request)})


def login_view(request: HttpRequest) -> JsonResponse:
    """Step 1: {username, password} -> {mfa_required: bool}."""
    if (denied := _method_not_allowed(request, "POST")) is not None:
        return denied
    data = _json_body(request)
    if data is None:
        return JsonResponse({"detail": "Request body must be JSON."}, status=400)
    user = authenticate(request, username=data.get("username"), password=data.get("password"))
    if user is None or not user.is_active:
        # Same message for unknown user and wrong password: no oracle.
        return JsonResponse({"detail": "Invalid credentials."}, status=400)
    mfa_required = begin_login(request, user)
    return JsonResponse({"mfa_required": mfa_required})


def mfa_view(request: HttpRequest) -> JsonResponse:
    """Step 2: {token} -> {} on success. Requires a pending step-1 login."""
    if (denied := _method_not_allowed(request, "POST")) is not None:
        return denied
    data = _json_body(request)
    if data is None:
        return JsonResponse({"detail": "Request body must be JSON."}, status=400)
    user = get_pending_mfa_user(request)
    if user is None:
        return JsonResponse({"detail": "No pending login. Log in first."}, status=400)
    if not confirmed_devices(user):
        # MFA was disabled mid-flow; fall back to a plain login.
        complete_mfa_login(request, user, None)
        return JsonResponse({})
    token = str(data.get("token") or "").strip()
    device = verify_mfa_token(user, token) if token else None
    if device is None:
        return JsonResponse(
            {"detail": "That code did not match. Try the current code."}, status=400
        )
    complete_mfa_login(request, user, device)
    return JsonResponse({})


def logout_view(request: HttpRequest) -> JsonResponse:
    if (denied := _method_not_allowed(request, "POST")) is not None:
        return denied
    auth_logout(request)
    return JsonResponse({})


def me_view(request: HttpRequest) -> JsonResponse:
    if (denied := _unauthenticated(request)) is not None:
        return denied
    return JsonResponse({"username": request.user.username})


def funds_view(request: HttpRequest) -> JsonResponse:
    if (denied := _unauthenticated(request)) is not None:
        return denied
    funds = Fund.objects.all().order_by("name")
    return JsonResponse(
        [
            {
                "id": fund.id,
                "name": fund.name,
                "vintage_year": fund.vintage_year,
                "status": fund.status,
            }
            for fund in funds
        ],
        safe=False,
    )


def fund_detail_view(request: HttpRequest, fund_id: int) -> JsonResponse:
    if (denied := _unauthenticated(request)) is not None:
        return denied
    try:
        fund = Fund.objects.prefetch_related("share_classes__commitments__investor", "loans").get(
            pk=fund_id
        )
    except Fund.DoesNotExist:
        return JsonResponse({"detail": "Not found."}, status=404)
    # ShareClass.Meta.ordering is ["rank"], so classes come out in payout order.
    return JsonResponse(
        {
            "id": fund.id,
            "name": fund.name,
            "vintage_year": fund.vintage_year,
            "status": fund.status,
            "share_classes": [
                {
                    "id": cls.id,
                    "name": cls.name,
                    "rank": cls.rank,
                    "commitments": [
                        {
                            "investor_name": c.investor.name,
                            # Hard rule 1: money travels as strings, never floats.
                            "amount": str(c.amount),
                        }
                        for c in cls.commitments.all()
                    ],
                }
                for cls in fund.share_classes.all()
            ],
            "loans": [
                {
                    "id": loan.id,
                    "borrower": loan.borrower_name,
                    "principal": str(loan.principal_amount),
                    "outstanding_balance": str(loan.outstanding_balance),
                    "status": loan.status,
                }
                for loan in fund.loans.all()
            ],
        }
    )
