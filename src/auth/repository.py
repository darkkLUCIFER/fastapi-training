from typing import Any
from collections.abc import Collection

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.dialects.postgresql import insert

from src.auth.models import User, Permission, RolePermission
from src.auth.constants import RoleChoices


__all__ = (
    'AuthRepository',
    'PermissionRepository',
)


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        self.db.add(user)
        return user

    def get_all(self) -> list[User]:
        return self.db.query(User).all()  # NOQA

    def get_one(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()  # NOQA

    def delete(self, user: User) -> None:
        self.db.delete(user)

    def exists(self, **filters: Any) -> bool:
        stmt = select(User.id).filter_by(**filters)
        return bool(self.db.scalar(select(stmt.exists())))

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()  # NOQA


class RolePermissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, role_permission: RolePermission) -> RolePermission:
        self.db.add(role_permission)
        return role_permission

    def delete(self, role_permission: RolePermission) -> None:
        self.db.delete(role_permission)

    def get_all_active_for_user(self, role: RoleChoices) -> list[str]:
        stmt = (
            select(Permission.key)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role == role, RolePermission.access.is_(True))  # NOQA
        )
        return list(self.db.scalars(stmt).all())

    def has_access(self, role: RoleChoices, permission_key: str) -> bool:
        stmt = (
            select(RolePermission.id)
            .join(Permission, RolePermission.permission_id == Permission.id)
            .where(
                RolePermission.role == role,  # NOQA
                RolePermission.access.is_(True),
                Permission.key == permission_key,  # NOQA
            )
            .limit(1)
        )
        return self.db.scalar(stmt) is not None

    def update_admin_permissions(self) -> int:
        permissions = self.db.scalars(select(Permission)).all()
        if not permissions:
            return 0

        existing_permission_ids = set(
            self.db.scalars(
                select(RolePermission.permission_id).where(RolePermission.role == RoleChoices.ADMIN)  # NOQA
            ).all()
        )
        missing_permission_ids = [
            permission.id for permission in permissions if permission.id not in existing_permission_ids
        ]
        if not missing_permission_ids:
            return 0

        statement = (
            insert(RolePermission)
            .values(
                [
                    {'role': RoleChoices.ADMIN, 'permission_id': permission_id}
                    for permission_id in missing_permission_ids
                ]
            )
            .on_conflict_do_nothing(
                index_elements=[RolePermission.role, RolePermission.permission_id],
            )
        )

        result = self.db.execute(statement)
        self.db.commit()

        return result.rowcount  # NOQA

    def get_all(self):
        return self.db.query(RolePermission).all()

    def get_by_id(self, role_permission_id: int) -> RolePermission:
        stmt = (
            select(RolePermission)
            .options(
                joinedload(RolePermission.permission),
            )
            .where(RolePermission.id == role_permission_id)  # NOQA
        )
        return self.db.scalar(stmt)


class PermissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_missing_permissions(self, keys: Collection[str]) -> int:
        if not keys:
            return 0
        statement = (
            insert(Permission)
            .values([{'key': key} for key in keys])
            .on_conflict_do_nothing(
                index_elements=[Permission.key],
            )
        )

        result = self.db.execute(statement)
        self.db.commit()

        return result.rowcount  # NOQA

    def get_all_permissions(self) -> list[Permission]:
        return self.db.query(Permission).all()  # NOQA
