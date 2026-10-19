"""Routes for the demo JSON API (increment 1.10)."""

from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path("auth/csrf/", views.csrf_view, name="csrf"),
    path("auth/login/", views.login_view, name="login"),
    path("auth/mfa/", views.mfa_view, name="mfa"),
    path("auth/logout/", views.logout_view, name="logout"),
    path("auth/me/", views.me_view, name="me"),
    path("funds/", views.funds_view, name="funds"),
    path("funds/<int:fund_id>/", views.fund_detail_view, name="fund-detail"),
]
