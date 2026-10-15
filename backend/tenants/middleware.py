"""Tenant middleware for Cascadia."""

from django.db import connection
from django.http import HttpRequest
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_public_schema_name, get_tenant_model


class TenantMiddleware(TenantMainMiddleware):
    """Selects the tenant schema from the request hostname.

    /healthz is exempt from hostname resolution: container probes, platform
    health checks, and CI smoke tests must get a 200 on a fresh database
    that has no tenants or domains yet. It is served from the public schema.
    Every other path still 404s on unknown hostnames.
    """

    def process_request(self, request: HttpRequest) -> None:
        if request.path == "/healthz":
            connection.set_schema_to_public()
            tenant = get_tenant_model()(schema_name=get_public_schema_name())
            request.tenant = tenant
            connection.set_tenant(tenant)
            return
        super().process_request(request)
