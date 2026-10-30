from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import HTTPException

from src.core import NotMatchError, SecurityUtils
from src.auth.models import User
from src.auth.schema import LoginUserSchema, RegisterUserSchema, RegisterSuperUserSchema
from src.core.config import settings
from src.auth.services import AuthService
from src.auth.constants import RoleChoices


@pytest.fixture
def auth_service():
    uow = MagicMock()
    uow.__enter__.return_value = uow
    security = MagicMock(spec=SecurityUtils)
    service = AuthService(uow=uow, security=security)
    return uow, security, service


def user(active=True):
    return User(
        id=12,
        username='ada',
        email='ada@example.com',
        hashed_password='password-hash',
        role=RoleChoices.USER,
        is_active=active,
    )


def registration(**overrides):
    values = {
        'username': 'ada',
        'email': 'ada@example.com',
        'password': 'password123',
        'password_confirmation': 'password123',
    }
    return RegisterUserSchema(**{**values, **overrides})


def test_register_user_hashes_password_and_commits(auth_service):
    uow, security, service = auth_service
    security.hash_password.return_value = 'secure-hash'
    uow.repository.exists.return_value = False

    result = service.register_user(registration())

    assert result.hashed_password == 'secure-hash'
    # The model's Python-side default is applied when SQLAlchemy flushes the row.
    assert User.__table__.c.role.default.arg == RoleChoices.USER
    security.hash_password.assert_called_once_with('password123')
    uow.repository.create.assert_called_once_with(result)
    uow.commit.assert_called_once_with()
    uow.refresh.assert_called_once_with(result)


def test_register_superuser_assigns_requested_role(auth_service):
    uow, security, service = auth_service
    security.hash_password.return_value = 'secure-hash'
    uow.repository.exists.return_value = False
    data = RegisterSuperUserSchema(**{**registration().model_dump(), 'role': 'admin'})

    result = service.register_user(data)

    assert result.role == RoleChoices.ADMIN


def test_register_rejects_duplicate_user_without_creating_or_committing(auth_service):
    uow, _, service = auth_service
    uow.repository.exists.return_value = True

    with pytest.raises(HTTPException) as error:
        service.register_user(registration())

    assert error.value.status_code == 400
    assert error.value.detail == 'duplicate user exists'
    uow.repository.create.assert_not_called()
    uow.commit.assert_not_called()


def test_login_returns_access_and_refresh_tokens(auth_service):
    uow, security, service = auth_service
    uow.repository.get_by_username.return_value = user()
    security.verify_password.return_value = True
    security.create_access_token.return_value = 'access'
    security.create_refresh_token.return_value = 'refresh'

    result = service.login_user(LoginUserSchema(username='ada', password='password123'))

    assert (result.access_token, result.refresh_token) == ('access', 'refresh')
    security.verify_password.assert_called_once_with('password123', 'password-hash')
    security.create_access_token.assert_called_once_with(subject='12', extra_claims={'username': 'ada', 'role': 'user'})


@pytest.mark.parametrize('found_user,password_valid', [(None, False), (True, False)])
def test_login_rejects_unknown_user_or_wrong_password(auth_service, found_user, password_valid):
    uow, security, service = auth_service
    uow.repository.get_by_username.return_value = user() if found_user else None
    security.verify_password.return_value = password_valid

    with pytest.raises(NotMatchError):
        service.login_user(LoginUserSchema(username='ada', password='password123'))


def test_refresh_rotates_refresh_token_and_revokes_old_jti(auth_service, monkeypatch):
    uow, security, service = auth_service
    monkeypatch.setattr(settings, 'jwt_refresh_rotation', True)
    security.decode_token.return_value = {'type': 'refresh', 'sub': '12', 'jti': 'old-jti'}
    security.is_refresh_revoked.return_value = False
    uow.repository.get_one.return_value = user()
    security.create_access_token.return_value = 'new-access'
    security.create_refresh_token.return_value = 'new-refresh'

    result = service.refresh_tokens('old-refresh')

    assert (result.access_token, result.refresh_token) == ('new-access', 'new-refresh')
    security.revoke_refresh_token.assert_called_once_with('old-jti')


def test_refresh_reuses_refresh_token_when_rotation_disabled(auth_service, monkeypatch):
    uow, security, service = auth_service
    monkeypatch.setattr(settings, 'jwt_refresh_rotation', False)
    security.decode_token.return_value = {'type': 'refresh', 'sub': '12', 'jti': 'jti'}
    uow.repository.get_one.return_value = user()
    security.create_access_token.return_value = 'new-access'

    result = service.refresh_tokens('original-refresh')

    assert result.refresh_token == 'original-refresh'
    security.revoke_refresh_token.assert_not_called()
    security.create_refresh_token.assert_not_called()


def test_refresh_rejects_access_token(auth_service):
    _, security, service = auth_service
    security.decode_token.return_value = {'type': 'access', 'sub': '12'}

    with pytest.raises(NotMatchError):
        service.refresh_tokens('access-token')


def test_refresh_rejects_invalid_or_expired_token(auth_service):
    _, security, service = auth_service
    security.decode_token.side_effect = jwt.ExpiredSignatureError('expired')

    with pytest.raises(NotMatchError):
        service.refresh_tokens('expired-token')


def test_refresh_rejects_revoked_token(auth_service, monkeypatch):
    _, security, service = auth_service
    monkeypatch.setattr(settings, 'jwt_refresh_rotation', True)
    security.decode_token.return_value = {'type': 'refresh', 'sub': '12', 'jti': 'revoked'}
    security.is_refresh_revoked.return_value = True

    with pytest.raises(NotMatchError):
        service.refresh_tokens('revoked-token')


@pytest.mark.parametrize('active_user', [None, False])
def test_refresh_rejects_missing_or_inactive_user(auth_service, active_user):
    uow, security, service = auth_service
    security.decode_token.return_value = {'type': 'refresh', 'sub': '12', 'jti': 'jti'}
    uow.repository.get_one.return_value = user(active=False) if active_user is False else None

    with pytest.raises(NotMatchError):
        service.refresh_tokens('refresh-token')
