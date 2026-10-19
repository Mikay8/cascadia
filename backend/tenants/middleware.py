"""Tenant middleware for Cascadia."""

from django.db import connection
from django.http import Http404, HttpRequest
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_public_schema_name, get_tenant_model, schema_context


class TenantMiddleware(TenantMainMiddleware):
    """Selects the tenant schema for the request.

    /healthz is exempt from hostname resolution: container probes, platform
    health checks, and CI smoke tests must get a 200 on a fresh database
    that has no tenants or domains yet. It is served from the public schema.

    /api/* additionally accepts an ``X-Tenant`` header naming a tenant schema.
    The demo React frontend is a different origin from the backend, so it
    cannot do hostname routing; the header lets it pick the tenant instead.
    The value is validated against existing tenants (unknown values 404), so
    it cannot select arbitrary schemas. Auth stays per-tenant -- users live
    in tenant schemas -- so the header cannot escalate across tenants. When
    the header is absent, /api/* falls back to hostname routing like the rest.

    Every other path still 404s on unknown hostnames.
    """

    def process_request(self, request: HttpRequest) -> None:
        if request.path == "/healthz":
            connection.set_schema_to_public()
            tenant = get_tenant_model()(schema_name=get_public_schema_name())
            request.tenant = tenant
            connection.set_tenant(tenant)
            return
        if request.path.startswith("/api/"):
            schema_name = request.headers.get("X-Tenant", "").strip()
            if schema_name:
                with schema_context(get_public_schema_name()):
                    tenant = get_tenant_model().objects.filter(schema_name=schema_name).first()
                if tenant is None:
                    raise Http404(f"Unknown tenant: {schema_name}")
                request.tenant = tenant
                connection.set_tenant(tenant)
                return
        super().process_request(request)
