"""Override wagtail views to use Gandi ID as the login provider."""
from django.conf.urls import url

from .views import Oauth2LoginView, Oauth2LogoutView


urlpatterns = [
    url(r"^login/$", Oauth2LoginView.as_view(), name="wagtailadmin_login"),
    url(r"^logout/$", Oauth2LogoutView.as_view(), name="wagtailadmin_logout"),
]
