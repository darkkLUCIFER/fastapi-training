from types import SimpleNamespace
from unittest.mock import MagicMock

from src.auth.models import User, Permission, RolePermission
from src.auth.constants import RoleChoices
from src.auth.repository import AuthRepository, PermissionRepository, RolePermissionRepository


def test_auth_repository_create_delete_and_basic_reads():
    session = MagicMock()
    repository = AuthRepository(session)
    user = User(username='ada', hashed_password='hash')

    assert repository.create(user) is user
    repository.get_all()
    repository.get_one(7)
    repository.get_by_username('ada')
    repository.delete(user)

    session.add.assert_called_once_with(user)
    assert session.query.call_count == 3
    session.delete.assert_called_once_with(user)


def test_auth_repository_exists_returns_boolean_from_scalar():
    session = MagicMock()
    session.scalar.return_value = 1

    assert AuthRepository(session).exists(username='ada') is True

    session.scalar.return_value = None
    assert AuthRepository(session).exists(username='missing') is False


def test_permission_repository_creates_only_missing_keys_and_lists():
    session = MagicMock()
    session.execute.return_value.rowcount = 2
    repository = PermissionRepository(session)

    assert repository.create_missing_permissions({'todo.create', 'todo.delete'}) == 2
    assert repository.create_missing_permissions(set()) == 0
    repository.get_all_permissions()

    session.execute.assert_called_once()
    session.query.assert_called_once_with(Permission)


def test_role_permission_repository_adds_and_deletes_records():
    session = MagicMock()
    repository = RolePermissionRepository(session)
    record = RolePermission(role=RoleChoices.USER, permission_id=3)

    assert repository.create(record) is record
    repository.delete(record)
    repository.get_all()

    session.add.assert_called_once_with(record)
    session.delete.assert_called_once_with(record)
    session.query.assert_called_once_with(RolePermission)


def test_role_permission_repository_returns_active_permission_keys():
    session = MagicMock()
    session.scalars.return_value.all.return_value = ['todo.create']

    result = RolePermissionRepository(session).get_all_active_for_user(RoleChoices.USER)

    assert result == ['todo.create']
    session.scalars.assert_called_once()


def test_role_permission_repository_checks_access():
    session = MagicMock()
    session.scalar.return_value = 4

    assert RolePermissionRepository(session).has_access(RoleChoices.ADMIN, 'todo.create') is True

    session.scalar.return_value = None
    assert RolePermissionRepository(session).has_access(RoleChoices.USER, 'todo.create') is False


def test_role_permission_repository_upserts_only_missing_admin_links():
    session = MagicMock()
    session.scalars.side_effect = [
        SimpleNamespace(all=lambda: [Permission(id=1, key='todo.create'), Permission(id=2, key='todo.delete')]),
        SimpleNamespace(all=lambda: [1]),
    ]
    session.execute.return_value.rowcount = 1

    result = RolePermissionRepository(session).update_admin_permissions()

    assert result == 1
    session.execute.assert_called_once()


def test_role_permission_repository_returns_zero_when_everything_is_already_linked():
    session = MagicMock()
    session.scalars.side_effect = [
        SimpleNamespace(all=lambda: [Permission(id=1, key='todo.create')]),
        SimpleNamespace(all=lambda: [1]),
    ]

    assert RolePermissionRepository(session).update_admin_permissions() == 0
    session.execute.assert_not_called()


def test_role_permission_repository_returns_zero_when_no_permissions_exist():
    session = MagicMock()
    session.scalars.return_value.all.return_value = []

    assert RolePermissionRepository(session).update_admin_permissions() == 0
    session.execute.assert_not_called()


def test_role_permission_repository_loads_permission_for_detail():
    session = MagicMock()
    expected = RolePermission(id=9, role=RoleChoices.USER, permission_id=3)
    session.scalar.return_value = expected

    assert RolePermissionRepository(session).get_by_id(9) is expected
    session.scalar.assert_called_once()
