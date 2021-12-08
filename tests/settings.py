USERS = {

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
