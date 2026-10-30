from datetime import UTC, datetime, timedelta

import jwt
import pytest

from src.core.config import settings
from src.core.services import SecurityUtils


@pytest.fixture(autouse=True)
def clear_revoked_tokens():
    SecurityUtils._revoked_refresh_jti.clear()
    yield
    SecurityUtils._revoked_refresh_jti.clear()


def test_password_hash_is_not_plain_text_and_can_be_verified():
    security = SecurityUtils()

    hashed = security.hash_password('correct horse battery staple')

    assert hashed != 'correct horse battery staple'
    assert security.verify_password('correct horse battery staple', hashed)
    assert not security.verify_password('wrong password', hashed)


def test_access_token_contains_standard_and_custom_claims():
    security = SecurityUtils()

    token = security.create_access_token('42', {'username': 'ada', 'role': 'user'})
    payload = security.decode_token(token)

    assert payload['sub'] == '42'
    assert payload['type'] == 'access'
    assert payload['username'] == 'ada'
    assert payload['role'] == 'user'
    assert payload['iat'] <= payload['exp']
    assert payload['jti']


def test_refresh_token_has_refresh_type_and_unique_identifier():
    security = SecurityUtils()

    first = security.decode_token(security.create_refresh_token('42'))
    second = security.decode_token(security.create_refresh_token('42'))

    assert first['sub'] == second['sub'] == '42'
    assert first['type'] == second['type'] == 'refresh'
    assert first['jti'] != second['jti']


def test_decode_rejects_expired_token(monkeypatch):
    security = SecurityUtils()
    monkeypatch.setattr(settings, 'jwt_access_token_expire_minutes', -1)

    token = security.create_access_token('42')

    with pytest.raises(jwt.ExpiredSignatureError):
        security.decode_token(token)


def test_decode_rejects_token_signed_with_another_secret(monkeypatch):
    security = SecurityUtils()
    token = security.create_access_token('42')
    monkeypatch.setattr(settings, 'jwt_secret_key', 'a-different-test-secret-that-is-long-enough')

    with pytest.raises(jwt.InvalidSignatureError):
        security.decode_token(token)


def test_refresh_token_revocation_is_tracked_by_jti():
    security = SecurityUtils()
    payload = security.decode_token(security.create_refresh_token('42'))

    assert not security.is_refresh_revoked(payload['jti'])
    security.revoke_refresh_token(payload['jti'])
    assert security.is_refresh_revoked(payload['jti'])


def test_created_token_expiration_uses_configured_lifetime(monkeypatch):
    monkeypatch.setattr(settings, 'jwt_access_token_expire_minutes', 12)
    payload = SecurityUtils.decode_token(SecurityUtils().create_access_token('42'))
    issued_at = datetime.fromtimestamp(payload['iat'], UTC)
    expires_at = datetime.fromtimestamp(payload['exp'], UTC)

    assert expires_at - issued_at == timedelta(minutes=12)
