"""Load settings for the wagtail-oauth2 app."""

from django.conf import settings

GLOBAL_PREFIX = "OAUTH2_"


def get_setting(name, default=None):
    """Get the settings without the prefix."""
    return getattr(settings, GLOBAL_PREFIX + name, default)
