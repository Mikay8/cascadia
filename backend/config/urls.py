from django.urls import include, path

from accounts.admin import site as admin_site
from config.views import healthz

urlpatterns = [
    path("admin/", admin_site.urls),
    path("accounts/", include("accounts.urls")),
    path("api/", include("api.urls")),
    path("healthz", healthz, name="healthz"),
]
