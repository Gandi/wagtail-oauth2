"""Load settings for the wagtail-oauth2 app."""
from django.conf import settings

global_prefix = "OAUTH2_"


def get_setting(name, default=None):
    """Get the settings without the prefix."""
    return getattr(settings, global_prefix + name, default)
