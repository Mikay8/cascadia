"""URL routes for login, MFA, and logout."""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("mfa/", views.mfa_view, name="mfa"),
    path("mfa/setup/", views.mfa_setup_view, name="mfa_setup"),
    path("logout/", views.logout_view, name="logout"),
]
