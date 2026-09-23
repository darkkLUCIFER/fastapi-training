from src.auth.services import PermissionSyncService
from src.auth.uow import PermissionUow
from src.core import SessionLocal


class PermissionSyncCli:
    @staticmethod
    def run() -> None:
        with SessionLocal() as db:
            service = PermissionSyncService(uow=PermissionUow(db))
            created_count = service.sync()

        print(f'Permissions synchronized. Created: {created_count}')


if __name__ == "__main__":
    PermissionSyncCli().run()
