import re

from django.contrib.auth.models import User

from wagtail_oauth2.views import gen_state_name, get_cookie_name, get_user_from_userinfo


def test_gen_state_name():
    state1 = gen_state_name()
    state2 = gen_state_name()
    assert state1 != state2
    assert re.match("[0-9a-z]{10}", state1)
    assert re.match("[0-9a-z]{10}", state2)


def test_get_cookie_name():
    return get_cookie_name("plop") == "oauth2.plop"


def test_get_user_from_userinfo_exists(user_mei):
    user = get_user_from_userinfo({"username": "mei"})
    assert user is not None
    assert isinstance(user, User)
    assert user == user_mei


def test_get_user_from_userinfo_does_not_exists(random_userinfo):
    user = get_user_from_userinfo(random_userinfo)
    assert user is not None
    assert isinstance(user, User)
    assert user.username == random_userinfo["username"]
    assert user.email == random_userinfo["email"]
    assert user.first_name == random_userinfo["first_name"]
    assert user.last_name == random_userinfo["last_name"]


def test_view_get(client, state):
    resp = client.get("/admin/login/")
    assert resp.status_code == 302
    redir = "https%3A%2F%2Ftestserver%2Fadmin%2Flogin%2F"
    assert (
        resp.headers["location"]
        == f"https://gandi.v5/authorize?client_id=Mei&redirect_uri={redir}&response_type=code&state={state}"
    )
    state_cookie = resp.cookies[get_cookie_name(state)]
    assert state_cookie.value == "/admin/"
