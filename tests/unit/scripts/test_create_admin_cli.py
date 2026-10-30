from contextlib import contextmanager
from unittest.mock import MagicMock

import pytest

from scripts import create_admin


def test_create_admin_cli_validates_input_and_registers_admin(monkeypatch, capsys):
    prompts = iter(['admin_user', 'admin@example.com'])
    passwords = iter(['strong-password', 'strong-password'])
    monkeypatch.setattr('builtins.input', lambda prompt: next(prompts))
    monkeypatch.setattr(create_admin.getpass, 'getpass', lambda prompt: next(passwords))
    db = MagicMock()

    @contextmanager
    def session_context():
        yield db

    monkeypatch.setattr(create_admin, 'SessionLocal', session_context)
    service = MagicMock()
    auth_service = MagicMock(return_value=service)
    monkeypatch.setattr(create_admin, 'AuthService', auth_service)
    security = MagicMock()
    monkeypatch.setattr(create_admin, 'SecurityUtils', lambda: security)

    create_admin.create_admin_user_cli()

    auth_service.assert_called_once()
    service.register_user.assert_called_once()
    registered_data = service.register_user.call_args.kwargs['data']
    assert registered_data.username == 'admin_user'
    assert registered_data.role == 'admin'
    assert 'created successfully' in capsys.readouterr().out


def test_create_admin_cli_exits_on_invalid_password_input(monkeypatch, capsys):
    prompts = iter(['admin_user', 'admin@example.com'])
    passwords = iter(['short', 'short'])
    monkeypatch.setattr('builtins.input', lambda prompt: next(prompts))
    monkeypatch.setattr(create_admin.getpass, 'getpass', lambda prompt: next(passwords))
    auth_service = MagicMock()
    monkeypatch.setattr(create_admin, 'AuthService', auth_service)

    with pytest.raises(SystemExit) as error:
        create_admin.create_admin_user_cli()

    assert error.value.code == 1
    assert 'Invalid input:' in capsys.readouterr().out
    auth_service.assert_not_called()
