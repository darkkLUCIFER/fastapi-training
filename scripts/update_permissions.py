from src.auth.services import PermissionSyncService, AuthorizationService
from src.auth.uow import PermissionUow, RolePermissionUow
from src.core import SessionLocal


class PermissionSyncCli:
    @staticmethod
    def run() -> None:
        with SessionLocal() as db:
            service = PermissionSyncService(uow=PermissionUow(db))
            created_permission_count = service.sync()

            authorization_service = AuthorizationService(uow=RolePermissionUow(db))
            created_admin_permissions_count = authorization_service.update_role_admin_permissions()

        print(f'Permissions synchronized. Created: {created_permission_count}')
        print(f'Admin Permissions synchronized. Created: {created_admin_permissions_count}')


if __name__ == "__main__":
    PermissionSyncCli().run()
