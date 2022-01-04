from unittest import mock
import pytest
from django.test import override_settings

from wagtail_oauth2.utils import get_access_token, save_tokens


@mock.patch("time.time", return_value=1000)
@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {},
            "tokens": {"access_token": "abc"},
            "expected": {},
        },
        {
            "settings": {"OAUTH2_STORE_TOKENS": True},
            "tokens": {"access_token": "abc"},
            "expected": {
                "wagtail_oauth2_access_token": "abc",
                "wagtail_oauth2_expires_at": 1900,
            },
        },
        {
            "settings": {"OAUTH2_STORE_TOKENS": True, "OAUTH2_DEFAULT_TTL": 42},
            "tokens": {"access_token": "abc"},
            "expected": {
                "wagtail_oauth2_access_token": "abc",
                "wagtail_oauth2_expires_at": 1042,
            },
        },
        {
            "settings": {"OAUTH2_STORE_TOKENS": True, "OAUTH2_DEFAULT_TTL": 42},
            "tokens": {"access_token": "abc", "expires_in": 300},
            "expected": {
                "wagtail_oauth2_access_token": "abc",
                "wagtail_oauth2_expires_at": 1300,
            },
        },
        {
            "settings": {"OAUTH2_STORE_TOKENS": True},
            "tokens": {
                "access_token": "abc",
                "refresh_token": "xyz",
                "expires_in": 300,
            },
            "expected": {
                "wagtail_oauth2_access_token": "abc",
                "wagtail_oauth2_refresh_token": "xyz",
                "wagtail_oauth2_expires_at": 1300,
            },
        },
    ],
)
def test_save_tokens(time, dummy_request_with_session, params):
    tokens = params["tokens"]
    settings = params["settings"]
    expected = params["expected"]
    with override_settings(**settings):
        save_tokens(dummy_request_with_session, tokens)
    assert dummy_request_with_session.session == expected


@mock.patch("time.time", return_value=1000)
@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {"OAUTH2_STORE_TOKENS": True},
            "session": {
                "wagtail_oauth2_access_token": "abc",
                "wagtail_oauth2_expires_at": 1300,
            },
            "expected": "abc",
        },
        {
            "settings": {"OAUTH2_STORE_TOKENS": True},
            "session": {
                "wagtail_oauth2_access_token": "abc",
                "wagtail_oauth2_expires_at": 300,
            },
            "expected": None,
        },
        {
            "settings": {"OAUTH2_STORE_TOKENS": False},
            "session": {
                "wagtail_oauth2_access_token": "abc",
                "wagtail_oauth2_expires_at": 1300,
            },
            "expected": None,
        },
        {
            # Expired Scenario
            "settings": {
                "OAUTH2_STORE_TOKENS": True,
            },
            "session": {
                "wagtail_oauth2_access_token": "abc",
                "wagtail_oauth2_refresh_token": "xyz",
                "wagtail_oauth2_expires_at": 300,
            },
            "expected": "toktok",
            "expected_new_session": {
                "wagtail_oauth2_access_token": "toktok",
                "wagtail_oauth2_expires_at": 4600,
                "wagtail_oauth2_refresh_token": "totoro",
            },
        },
    ],
)
def test_get_access_token(time, mock_oauth2, dummy_request_with_session, params):
    settings = params["settings"]
    with override_settings(**settings):
        token = get_access_token(dummy_request_with_session)
    assert token == params["expected"]
    if "expected_new_session" in params:
        assert dummy_request_with_session.session == params["expected_new_session"]
