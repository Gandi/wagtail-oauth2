import logging

from urllib.parse import urlencode

import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout

from .settings import get_setting

log = logging.getLogger(__name__)


class Token(object):
    @classmethod
    def by_authcode(cls, auth_code):
        try:
            token_url = get_setting("TOKEN_URL")
            log.info("Fetching token on %s/token" % token_url)
            response = requests.post(
                token_url,
                data={
                    "client_id": get_setting("CLIENT_ID"),
                    "client_secret": get_setting("CLIENT_SECRET"),
                    "grant_type": "authorization_code",
                    "code": auth_code,
                },
                verify=get_setting("VERIFY_CERTIFICATE"),
                timeout=get_setting("TIMEOUT"),
            )
            response.raise_for_status()
            return response.json()

        except (ConnectionError, TimeoutError, Timeout) as exc:
            log.error("OAuth2 server is down: %s" % exc.__class__.__name__)
        except HTTPError as exc:
            if exc.response.status_code >= 500:
                log.error(
                    "OAuth2 server is not working properly? got %s"
                    % exc.response.status_code
                )
            else:
                log.error("Cannot retrieve token: %s" % exc.response.text)
        except Exception:
            log.exception(
                "Unexpected exception while retrieving token using "
                "authorization code"
            )
        return {}

    @classmethod
    def get_authenticated_url(cls, login_url, state):
        data = {
            "client_id": get_setting("CLIENT_ID"),
            "redirect_uri": login_url,
            "response_type": "code",
            "state": state,
        }
        return "{}?{}".format(
            get_setting("AUTH_URL"), urlencode(data, doseq=True)
        )

    @classmethod
    def by_refresh_token(cls, refresh_token):
        try:
            token_url = get_setting("TOKEN_URL")
            log.info("Refreshing token on %s/token" % token_url)
            response = requests.post(
                token_url,
                data={
                    "client_id": get_setting("CLIENT_ID"),
                    "client_secret": get_setting("CLIENT_SECRET"),
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                verify=get_setting("VERIFY_CERTIFICATE"),
                timeout=get_setting("TIMEOUT"),
            )
            response.raise_for_status()
            tokens = response.json()
            return tokens
        except (ConnectionError, TimeoutError, Timeout) as exc:
            log.error("OAuth2 server is down: %s" % exc.__class__.__name__)
        except HTTPError as exc:
            if 400 <= exc.response.status_code < 500:
                log.warning(
                    "OAuth2 server does not refresh the token (%s: %s), "
                    "force disconnect",
                    exc.response.status_code,
                    exc.response.text,
                )
            elif 500 <=exc.response.status_code < 600:
                log.error(
                    "OAuth2 server is not working properly? got %s",
                    exc.response.status_code,
                )
        except Exception:
            log.exception(
                "Unexpected exception while retrieving token using refresh token"
            )
        return {}
