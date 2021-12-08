import os
import os.path
from typing import Dict, Any

USERS = {
    "mey_authcode": {
        "username": "mei",
    }
}

def load_userinfo(access_token):
    """
    Load userinfo from access token.

    Return a dict containing username, email, first_name, last_name, and
    is_superuser fields to register any new user.
    """
    return USERS.get(access_token, {})


OAUTH2_VERIFY_CERTIFICATE = False
OAUTH2_TIMEOUT = 30

OAUTH2_LOAD_USERINFO = load_userinfo

OAUTH2_CLIENT_ID = "Mei"
OAUTH2_CLIENT_SECRET = "T0t0r0"

OAUTH2_AUTH_URL = "https://gandi.v5/authorize"
OAUTH2_TOKEN_URL = "https://gandi.v5/token"
OAUTH2_LOGOUT_URL = "https://gandi.v5/logout"
OAUTH2_USERINFO_URL = "https://gandi.v5/tokeninfo"


ROOT_URLCONF = "wagtail_oauth2.tests.urls"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_KEY = "beep"

DATABASES: Dict[str, Dict[str, Any]] = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "test.db"),
        "TEST": {
            "NAME": "test.db",
        },
    },
}


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "wagtail_oauth2",
    "wagtail.admin",
    "wagtail.users",
    "wagtail.core",
    "tests",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware"
]


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
    }
]
