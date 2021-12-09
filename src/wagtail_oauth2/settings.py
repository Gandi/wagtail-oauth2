from django.conf import settings

global_prefix = "OAUTH2_"


def get_setting(name, default=None):
    return getattr(settings, global_prefix + name, default)
