import logging
import time
from typing import Optional, cast

from .resources import Token
from .settings import GLOBAL_PREFIX, get_setting

log = logging.getLogger(__name__)

DEFAULT_SESSION_KEY_PREFIX = "wagtail_oauth2_"


def save_tokens(request, tokens):
    if not get_setting("STORE_TOKENS", False):
        log.warning(
            f"{GLOBAL_PREFIX}_STORE_TOKENS is not set to true, cannot retrieve token"
        )
        return None
    prefix = get_setting("SESSION_KEY_PREFIX", DEFAULT_SESSION_KEY_PREFIX)
    request.session[f"{prefix}access_token"] = tokens["access_token"]
    if "refresh_token" in tokens:
        request.session[f"{prefix}refresh_token"] = tokens["refresh_token"]
    if "expires_in" in tokens:
        request.session[f"{prefix}expires_at"] = int(time.time() + tokens["expires_in"])
    else:
        request.session[f"{prefix}expires_at"] = int(
            time.time() + cast(float, get_setting("DEFAULT_TTL", 15 * 60))  # 15 minutes
        )


def get_access_token(request) -> Optional[str]:
    """Get the access token, or fetch a new one if it is possible, otherwise return None."""
    if not get_setting("STORE_TOKENS", False):
        log.warning(
            f"{GLOBAL_PREFIX}_STORE_TOKENS is not set to true, cannot retrieve token"
        )
        return None

    prefix = get_setting("SESSION_KEY_PREFIX", DEFAULT_SESSION_KEY_PREFIX)
    access_token = request.session.get(f"{prefix}access_token")
    refresh_token = request.session.get(f"{prefix}refresh_token")
    expires_at = int(request.session.get(f"{prefix}expires_at", 0))

    if access_token and expires_at > time.time():
        return access_token

    if refresh_token:
        log.info("Refreshing token")
        tokens = Token.by_refresh_token(refresh_token)
        if tokens:
            save_tokens(request, tokens)
            log.info("Getting the new token %s***", access_token[:6])
            return tokens["access_token"]
