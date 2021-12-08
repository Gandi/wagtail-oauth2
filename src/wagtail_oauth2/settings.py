from django.conf import settings

global_prefix = "OAUTH2_"


def get_setting(name):
    return getattr(settings, global_prefix + name)
