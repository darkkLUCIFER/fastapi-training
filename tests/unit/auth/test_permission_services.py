from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.auth.schema import CreateRolePermissionSchema, UpdateRolePermissionSchema
from src.auth.services import (
    PermissionService,
    AuthorizationService,
    PermissionSyncService,
    RolePermissionService,
)
from src.auth.constants import RoleChoices
from src.core.exceptions import NotFoundError
from src.auth.constants.permission import PermissionChoices


def make_uow():
    uow = MagicMock()
    uow.__enter__.return_value = uow
    return uow


def test_authorization_returns_known_active_permissions_and_ignores_unknown_keys():
    uow = make_uow()
    uow.repository.get_all_active_for_user.return_value = [PermissionChoices.TODO_CREATE.value, 'future.permission']
    service = AuthorizationService(uow)

    permissions = service.get_permissions(SimpleNamespace(role=RoleChoices.USER))

    assert permissions == frozenset({PermissionChoices.TODO_CREATE})


def test_authorization_returns_none_when_no_known_permissions_exist():
    uow = make_uow()
    uow.repository.get_all_active_for_user.return_value = ['unknown.permission']

    assert AuthorizationService(uow).get_permissions(SimpleNamespace(role=RoleChoices.USER)) is None


def test_authorization_checks_exact_permission_key():
    uow = make_uow()
    uow.repository.has_access.return_value = True

    allowed = AuthorizationService(uow).has_permission(
        SimpleNamespace(role=RoleChoices.ADMIN), PermissionChoices.TODO_CREATE
    )

    assert allowed is True
    uow.repository.has_access.assert_called_once_with(
        role=RoleChoices.ADMIN, permission_key=PermissionChoices.TODO_CREATE.value
    )


def test_permission_sync_commits_all_declared_permission_keys():
    uow = make_uow()
    uow.repository.create_missing_permissions.return_value = 4

    result = PermissionSyncService(uow).sync()

    assert result == 4
    synced_keys = uow.repository.create_missing_permissions.call_args.args[0]
    assert synced_keys == {choice.value for choice in PermissionChoices}
    uow.commit.assert_called_once_with()


def test_permission_service_lists_permissions():
    uow = make_uow()
    permissions = [SimpleNamespace(key='todo.create')]
    uow.repository.get_all_permissions.return_value = permissions

    assert PermissionService(uow).list_all_permissions() == permissions


def test_role_permission_service_creates_updates_and_deletes_records():
    uow = make_uow()
    service = RolePermissionService(uow)
    created = service.create_role_permission(CreateRolePermissionSchema(role=RoleChoices.USER, permission_id=3))
    assert created.role == RoleChoices.USER
    uow.repository.create.assert_called_once_with(role_permission=created)
    uow.commit.assert_called_once_with()

    uow.reset_mock()
    existing = SimpleNamespace(role=RoleChoices.USER, permission_id=3, access=True)
    uow.repository.get_by_id.return_value = existing
    updated = service.update_role_permission(
        8, UpdateRolePermissionSchema(role=RoleChoices.ADMIN, permission_id=3, access=False)
    )
    assert updated.access is False
    assert updated.role == RoleChoices.ADMIN
    uow.commit.assert_called_once_with()
    uow.refresh.assert_called_once_with(existing)

    uow.reset_mock()
    uow.repository.get_by_id.return_value = existing
    service.delete_role_permission(8)
    uow.repository.delete.assert_called_once_with(role_permission=existing)
    uow.commit.assert_called_once_with()


def test_role_permission_service_raises_not_found_for_missing_record():
    uow = make_uow()
    uow.repository.get_by_id.return_value = None

    with pytest.raises(NotFoundError, match='RolePermission with id: 8 not found'):
        RolePermissionService(uow).get_role_permission(8)
