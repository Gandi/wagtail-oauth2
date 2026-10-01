import logging

import requests
from django.conf import settings
from django.http.request import HttpRequest
from django.shortcuts import redirect

from wagtail_oauth2.settings import GLOBAL_PREFIX, get_setting
from wagtail_oauth2.utils import get_access_token

log = logging.getLogger(__name__)


class KeepAliveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):

        login_url = f"{settings.WAGTAILADMIN_BASE_URL}/admin/login/"
        if request.path == "/admin/login/":
            return self.get_response(request)

        url = get_setting("USERINFO_URL", "")
        if not url:
            log.error(f"Missing setting {GLOBAL_PREFIX}_USERINFO_URL")
        else:
            access_token = get_access_token(request)
            try:
                response = requests.get(
                    url,  # type: ignore
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
            except Exception:
                return redirect(login_url)

        return self.get_response(request)
