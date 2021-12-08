import pytest

from wagtail_oauth2.resources import Token


def test_token_by_authcode(mock_oauth2):
    tokens = Token.by_authcode("codecode")
    assert tokens == {
        "access_token": "mey_authcode",
        "refresh_token": "freshmenthol",
    }
    assert mock_oauth2.api_calls == {
        (
            "post",
            "https://gandi.v5/token~client_id=Mei&client_secret=T0t0r0&code=codecode&grant_type=authorization_code",
        ): [
            {
                "data": {
                    "client_id": "Mei",
                    "client_secret": "T0t0r0",
                    "code": "codecode",
                    "grant_type": "authorization_code",
                },
                "json": None,
                "timeout": 30,
                "verify": False,
            }
        ]
    }


@pytest.mark.parametrize("authcode", ["badcode", "e500", "TimeoutError", "ConnectionError", "RuntimeError"])
def test_token_by_authcode_unkown_user(authcode, mock_oauth2):
    tokens = Token.by_authcode(authcode)
    assert tokens == {}


def test_get_authenticated_url():
    url = Token.get_authenticated_url("http://my.cms", "abahoui")
    assert (
        url
        == "https://gandi.v5/authorize?client_id=Mei&redirect_uri=http%3A%2F%2Fmy.cms&response_type=code&state=abahoui"
    )


def test_by_refresh_token(mock_oauth2):
    tokens = Token.by_refresh_token("freshmenthol")
    assert tokens == {
        "access_token": "def",
        "refresh_token": "freshmenthol",
    }
    assert mock_oauth2.api_calls == {
        (
            "post",
            "https://gandi.v5/token~client_id=Mei&client_secret=T0t0r0&grant_type=refresh_token&refresh_token=freshmenthol",
        ): [
            {
                "data": {
                    "client_id": "Mei",
                    "client_secret": "T0t0r0",
                    "grant_type": "refresh_token",
                    "refresh_token": "freshmenthol",
                },
                "json": None,
                "timeout": 30,
                "verify": False,
            }
        ]
    }

@pytest.mark.parametrize("refresh_troken", ["e409", "e500", "TimeoutError", "ConnectionError", "RuntimeError"])
def test_by_refresh_token_4xx(refresh_troken, mock_oauth2):
    tokens = Token.by_refresh_token(refresh_troken)
    assert tokens == {}
