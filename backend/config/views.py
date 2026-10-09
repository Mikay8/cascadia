from django.http import HttpRequest, JsonResponse


def healthz(request: HttpRequest) -> JsonResponse:
    """Liveness check for the platform. Touches no tenant data."""
    return JsonResponse({"status": "ok"})
