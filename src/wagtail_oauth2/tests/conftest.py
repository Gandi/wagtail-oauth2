import json
from collections import defaultdict
from io import BytesIO
from typing import Any, Dict, Tuple
from unittest import mock
from urllib.parse import urlencode

import pytest
from django.contrib.auth import get_user_model
from faker import Faker
from requests import Response

fake = Faker()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def user_mei():
    user_cls = get_user_model()
    try:
        user = user_cls.objects.get(username="mei")
    except user_cls.DoesNotExist:
        user = user_cls()
        user.username = "mei"
        user.is_staff = True
        user.email = "mei@toto.ro"
        user.first_name = "Mei"
        user.last_name = "Kusakabe"
        user.is_superuser = True
        user.save()
    return user


@pytest.fixture
def random_userinfo():
    return {
        "username": f"{fake.user_name()}_{fake.pystr(4, 4)}",
        "is_staff": True,
        "email": fake.email(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "is_superuser": True,
    }


API_RESPONSE: Dict[Tuple[str, str], Tuple[int, Any, Any]] = {
    (
        "post",
        "https://gandi.v5/token~client_id=Mei&client_secret=T0t0r0&code=codecode&grant_type=authorization_code",
    ): (
        200,
        # Headers
        {},
        # Body
        {"access_token": "mey_accesstoken", "refresh_token": "freshmenthol"},
    ),
    (
        "post",
        "https://gandi.v5/token~client_id=Mei&client_secret=T0t0r0&code=badcode&grant_type=authorization_code",
    ): (
        400,
        # Headers
        {},
        # Body
        {"error": "invalid_token"},
    ),
    (
        "post",
        "https://gandi.v5/token~client_id=Mei&client_secret=T0t0r0&code=e500&grant_type=authorization_code",
    ): (
        500,
        # Headers
        {},
        # Body
        {"error": "server_error"},
    ),
    (
        "post",
        "https://gandi.v5/token~client_id=Mei&client_secret=T0t0r0&grant_type=refresh_token&refresh_token=freshmenthol",
    ): (
        200,
        # Headers
        {},
        # Body
        {"access_token": "def", "refresh_token": "freshmenthol"},
    ),
    (
        "post",
        "https://gandi.v5/token~client_id=Mei&client_secret=T0t0r0&grant_type=refresh_token&refresh_token=e409",
    ): (
        409,
        # Headers
        {},
        # Body
        {},
    ),
    (
        "post",
        "https://gandi.v5/token~client_id=Mei&client_secret=T0t0r0&grant_type=refresh_token&refresh_token=e500",
    ): (
        500,
        # Headers
        {},
        # Body
        {},
    ),
}


class DummyResponse(Response):
    """Represent a requests response."""

    def __init__(self, body="", status_code=200, headers=None):
        super(DummyResponse, self).__init__()
        self.raw = BytesIO(body.encode("utf-8"))
        self.status_code = status_code
        self.headers = headers or {}


class RequestsMock(mock.Mock):
    """A mock for request calls."""

    api_calls = defaultdict(list)

    def __init__(
        self,
        api_response,
        missing_status=503,
        missing_body="Internal Server Error",
    ):
        api_response = api_response

        def fake_api(method, url, **kwargs):
            get_params = sorted(kwargs.get("params", {}).items())
            if get_params:
                url += "?" + urlencode(get_params)
            post_params = sorted(kwargs.get("data", {}).items())
            if post_params:
                url += "~" + urlencode(post_params)

            if "TimeoutError" in url:
                raise TimeoutError("Boom")

            if "ConnectionError" in url:
                raise ConnectionError("Boom")

            if "RuntimeError" in url:
                raise RuntimeError("Sometime things fails")

            if (method, url) in api_response:
                status, headers, res = api_response[(method, url)]
                res = json.dumps(res)
            else:
                print(f"{method} {url} is missing returning missing results")
                status, headers, res = missing_status, None, missing_body
            RequestsMock.api_calls[(method, url)].append(kwargs)
            return DummyResponse(res, status, headers)

        super(RequestsMock, self).__init__(side_effect=fake_api)


@pytest.fixture()
def mock_oauth2():
    mock_req = mock.patch(
        "requests.Session.request",
        RequestsMock(API_RESPONSE),
    )
    mock_req.start()
    yield RequestsMock
    mock_req.stop()
    RequestsMock.api_calls.clear()


@pytest.fixture()
def state():
    state = fake.pystr(4, 4)
    with mock.patch("wagtail_oauth2.views.gen_state_name", return_value=state):
        yield state


@pytest.fixture()
def auth_code(mock_oauth2):
    return "codecode"
