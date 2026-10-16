"""Enforces the absolute session timeout (increment 1.4).

Django's SESSION_COOKIE_AGE plus SESSION_SAVE_EVERY_REQUEST gives us a
sliding 30-minute *idle* timeout, enforced both by the cookie max-age and by
the server-side session expiry. This middleware adds the *absolute* cap: a
session ends CASCADIA_ABSOLUTE_SESSION_TIMEOUT seconds after login no matter
how active the user is. The login timestamp is stored server-side in the
session, so it cannot be forged by the client.
"""

import time

from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

SESSION_STARTED_AT_KEY = "_cascadia_session_started_at"


def _absolute_timeout_seconds() -> int:
    return int(getattr(settings, "CASCADIA_ABSOLUTE_SESSION_TIMEOUT", 30 * 60))


class AbsoluteSessionTimeoutMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest) -> HttpResponse | None:
        if not request.user.is_authenticated:
            return None
        now = time.time()
        started_at = request.session.get(SESSION_STARTED_AT_KEY)
        if started_at is None:
            # First authenticated request of this session: start the clock.
            request.session[SESSION_STARTED_AT_KEY] = now
            return None
        if now - float(started_at) > _absolute_timeout_seconds():
            logout(request)
        return None
