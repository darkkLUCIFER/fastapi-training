from typing import Any
from collections.abc import Collection

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from src.auth.models import User, Permission, RolePermission


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

    def get_all_for_user(self, role: str) -> list[str]:
        columns = [RolePermission.permission_id.op('->')('key')]
        rows = self.db.query(*columns).filter(RolePermission.role == role).all()  # NOQA
        return [r[0] for r in rows]


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
