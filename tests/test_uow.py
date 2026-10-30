import unittest
from unittest.mock import MagicMock

from src.auth.uow import PermissionUow, RolePermissionUow
from src.auth.services import AuthorizationService, PermissionSyncService
from src.core.database.uow import BaseUow


class BaseUowTests(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.session.in_transaction.return_value = False
        self.uow = BaseUow(self.session)

    def test_uncommitted_work_is_rolled_back_on_normal_exit(self):
        with self.uow:
            pass

        self.session.rollback.assert_called_once_with()
        self.session.commit.assert_not_called()

    def test_committed_work_is_not_rolled_back_on_normal_exit(self):
        with self.uow:
            self.uow.commit()

        self.session.commit.assert_called_once_with()
        self.session.rollback.assert_not_called()

    def test_transaction_opened_after_commit_is_closed_on_exit(self):
        self.session.in_transaction.return_value = True

        with self.uow:
            self.uow.commit()

        self.session.commit.assert_called_once_with()
        self.session.rollback.assert_called_once_with()

    def test_exception_rolls_back_and_propagates(self):
        with self.assertRaisesRegex(RuntimeError, 'failed'), self.uow:
            raise RuntimeError('failed')

        self.session.rollback.assert_called_once_with()


class PermissionTransactionTests(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.session.in_transaction.return_value = False

    def test_permission_sync_commits_in_service(self):
        uow = PermissionUow(self.session)
        uow.repository.create_missing_permissions = MagicMock(return_value=3)

        result = PermissionSyncService(uow).sync()

        self.assertEqual(result, 3)
        self.session.commit.assert_called_once_with()
        self.session.rollback.assert_not_called()

    def test_admin_permission_update_commits_in_service(self):
        uow = RolePermissionUow(self.session)
        uow.repository.update_admin_permissions = MagicMock(return_value=2)

        result = AuthorizationService(uow).update_role_admin_permissions()

        self.assertEqual(result, 2)
        self.session.commit.assert_called_once_with()
        self.session.rollback.assert_not_called()


if __name__ == '__main__':
    unittest.main()
