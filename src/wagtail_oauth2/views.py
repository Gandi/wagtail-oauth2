"""
Views to log in using an OAuth2.0 Authorization Server.

Currently, we do not keep the access and refresh token in the session,
because it is not necessary.

It could be done later to retrieve data from API using OAuth2 authorizations.
"""
import binascii
import logging
import os

from django.conf import settings
from django.contrib.auth import get_user_model, login as auth_login
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.urls import reverse
from wagtail.admin.views.account import LoginView, LogoutView

from .resources import Token
from .settings import get_setting


log = logging.getLogger(__name__)


def gen_state_name():
    """Generate a random state name."""
    return binascii.hexlify(os.urandom(5)).decode("ascii")


def get_cookie_name(state):
    """Generate the cookie name for the OAuth2.0 state."""
    return f"oauth.{state}"


class StateError(ValueError):
    """raised in case the oauth2 state workflow is not valid."""


def get_user_from_userinfo(userinfo):
    """Create or retrieve a user from the wagtail point of view, from the userinfo."""
    username = userinfo["username"]
    user_cls = get_user_model()
    try:
        user = user_cls.objects.get(username=username)
    except user_cls.DoesNotExist:
        # Create a new user. There's no need to set a password
        # because only the password from settings.py is checked.
        user = user_cls(username=username)

        user.is_staff = userinfo.get("is_staff", True)
        user.email = userinfo.get("email")
        user.first_name = userinfo.get("first_name")
        user.last_name = userinfo.get("last_name")
        user.is_superuser = userinfo["is_superuser"]
        user.save()
        if not user.is_superuser:
            groups = userinfo.get("groups", ["Moderators", "Editors"])
            for group_name in groups:
                group = Group.objects.filter(name=group_name).first()
                group.user_set.add(user)
                group.save()
    return user


class Oauth2LoginView(LoginView):
    """Login view."""

    template_name = "login_error.html"

    def add_state(self, request, resp, state):
        """Set the OAuth2.0 state in the cookie."""
        default = "/admin"
        if getattr(settings, "WAGTAIL_APPEND_SLASH", True):
            default += "/"
        referrer = request.GET.get("next", self.get_success_url())
        # never use the login form itself as referrer
        if referrer.startswith(reverse("wagtailadmin_login")):
            referrer = default
        if not referrer.startswith("/"):
            referrer = default

        host = request.get_host()
        resp.set_cookie(
            get_cookie_name(state),
            referrer,
            max_age=300,
            secure=not host.startswith("localhost:"),
            httponly=True,
        )
        return resp

    def check_state(self, request):
        """Verify that the OAuth2.0 state in the cookie match callback query."""
        state = request.GET.get("state")
        if not state:
            raise StateError("Missing OAuth2 state")
        cookie_name = get_cookie_name(state)
        if cookie_name not in request.COOKIES:
            raise StateError("Invalid OAuth2 state")
        return request.COOKIES[cookie_name]

    def start_oauth2_dance(self, request, state):
        """Create the http query that redirect to the OAuth2.0"""
        log.info("Redirect to the oauth2 authorization server")
        host = request.get_host()
        # XXX request.scheme does not works properly, maybe a config issue
        scheme = "http" if host.startswith("localhost:") else "https"
        url = Token.get_authenticated_url(
            scheme + "://" + host + reverse("wagtailadmin_login"),
            state,
        )
        return redirect(url)

    def consume_oauth2_code(self, request, redirect_uri):
        """Retrieve a bearer token from the authorization code, log the user."""
        log.info("Consume the code")
        token = Token.by_authcode(request.GET["code"])

        userinfo = get_setting("LOAD_USERINFO")(token["access_token"])
        user = get_user_from_userinfo(userinfo)
        auth_login(self.request, user)
        return redirect(redirect_uri)

    def render_error(self, error, error_description):
        """Render the template to diplay error to the user."""
        return self.render_to_response(
            {
                "error": error,
                "error_description": error_description,
            }
        )

    def get(self, request, *args, **kwargs):
        """Handle HTTP GET query."""
        redirect_uri = ""
        if "code" in request.GET or "error" in request.GET:
            try:
                redirect_uri = self.check_state(request)
            except StateError as exc:
                return self.render_error("OAuth 2 Security Error", str(exc))

        if "code" in request.GET:
            return self.consume_oauth2_code(request, redirect_uri)
        elif "error" in request.GET:
            log.info("OAuth2 server error")
            return self.render_error(
                request.GET["error"],
                request.GET.get("error_description"),
            )
        else:
            state = gen_state_name()
            return self.add_state(
                request, self.start_oauth2_dance(request, state), state
            )


class Oauth2LogoutView(LogoutView):
    """Logout view."""

    def dispatch(self, request, *args, **kwargs):
        """Handle every HTTP Query to logout user."""

        logout_url = get_setting("LOGOUT_URL")
        if logout_url:
            resp = redirect(logout_url)
        else:
            resp = super().dispatch(request, *args, **kwargs)

        # XXX sthis code code has been copy from Wagtail.

        # By default, logging out will generate a fresh sessionid cookie. We want to use the
        # absence of sessionid as an indication that front-end pages are being viewed by a
        # non-logged-in user and are therefore cacheable, so we forcibly delete the cookie here.
        resp.delete_cookie(
            settings.SESSION_COOKIE_NAME,
            domain=settings.SESSION_COOKIE_DOMAIN,
            path=settings.SESSION_COOKIE_PATH,
        )

        # HACK: pretend that the session hasn't been modified, so that SessionMiddleware
        # won't override the above and write a new cookie.
        self.request.session.modified = False
        return resp
