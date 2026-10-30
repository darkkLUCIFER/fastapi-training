from unittest.mock import MagicMock

from scripts.update_permissions import PermissionSyncCli
import scripts.update_permissions as update_permissions


def test_permission_sync_cli_runs_both_sync_services(monkeypatch):
    db = MagicMock()
    session_factory = MagicMock()
    session_factory.return_value.__enter__.return_value = db
    monkeypatch.setattr(update_permissions, 'SessionLocal', session_factory)

    permission_sync = MagicMock()
    permission_sync.sync.return_value = 5
    permission_sync_factory = MagicMock(return_value=permission_sync)
    monkeypatch.setattr(update_permissions, 'PermissionSyncService', permission_sync_factory)

    authorization = MagicMock()
    authorization.update_role_admin_permissions.return_value = 3
    authorization_factory = MagicMock(return_value=authorization)
    monkeypatch.setattr(update_permissions, 'AuthorizationService', authorization_factory)

    PermissionSyncCli.run()

    permission_sync.sync.assert_called_once_with()
    authorization.update_role_admin_permissions.assert_called_once_with()
    permission_sync_factory.assert_called_once()
    authorization_factory.assert_called_once()
