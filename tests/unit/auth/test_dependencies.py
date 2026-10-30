from types import SimpleNamespace
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.core.config import settings
from src.auth.dependencies import get_current_user, get_current_payload


def credentials(token, scheme='Bearer'):
    return HTTPAuthorizationCredentials(scheme=scheme, credentials=token)


def test_current_payload_rejects_missing_credentials():
    with pytest.raises(HTTPException) as error:
        get_current_payload(None, MagicMock())

    assert error.value.status_code == 401
    assert error.value.headers['WWW-Authenticate'] == settings.jwt_token_location


def test_current_payload_rejects_unexpected_auth_scheme():
    with pytest.raises(HTTPException, match='Invalid auth scheme'):
        get_current_payload(credentials('token', scheme='Basic'), MagicMock())


def test_current_payload_rejects_invalid_token():
    security = MagicMock()
    security.decode_token.side_effect = jwt.InvalidTokenError('invalid')

    with pytest.raises(HTTPException) as error:
        get_current_payload(credentials('invalid'), security)

    assert error.value.status_code == 401
    assert error.value.detail == 'Invalid or expired token'


def test_current_payload_requires_access_token():
    security = MagicMock()
    security.decode_token.return_value = {'type': 'refresh'}

    with pytest.raises(HTTPException) as error:
        get_current_payload(credentials('refresh'), security)

    assert error.value.status_code == 401
    assert error.value.detail == 'Access token required'


def test_current_payload_returns_decoded_access_claims():
    security = MagicMock()
    security.decode_token.return_value = {'type': 'access', 'sub': '3'}

    assert get_current_payload(credentials('valid'), security) == {'type': 'access', 'sub': '3'}


@pytest.mark.parametrize('found_user', [None, SimpleNamespace(is_active=False)])
def test_current_user_rejects_missing_or_inactive_accounts(found_user):
    service = SimpleNamespace(uow=SimpleNamespace(repository=SimpleNamespace(get_one=lambda user_id: found_user)))

    with pytest.raises(HTTPException) as error:
        get_current_user({'sub': '3'}, service)

    assert error.value.status_code == 401
    assert error.value.detail == 'User not found or inactive'


def test_current_user_returns_active_account():
    user = SimpleNamespace(is_active=True)
    service = SimpleNamespace(uow=SimpleNamespace(repository=SimpleNamespace(get_one=lambda user_id: user)))

    assert get_current_user({'sub': '3'}, service) is user
