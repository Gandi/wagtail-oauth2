"""Override wagtail views to use Gandi ID as the login provider."""
from django.urls import re_path

from .views import Oauth2LoginView, Oauth2LogoutView


urlpatterns = [
    re_path(r"^login/$", Oauth2LoginView.as_view(), name="wagtailadmin_login"),
    re_path(r"^logout/$", Oauth2LogoutView.as_view(), name="wagtailadmin_logout"),
]
"""Url to load in the app."""
