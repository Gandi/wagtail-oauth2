from django.urls import include, path

from wagtail.admin import urls as wagtailadmin_urls
from wagtail_oauth2 import urls as oauth2_urls

urlpatterns = [
    # /!\ must appears before admin/ to override the login part
    path("admin/", include(oauth2_urls)),
    path("admin/", include(wagtailadmin_urls)),
]
