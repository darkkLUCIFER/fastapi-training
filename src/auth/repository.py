from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.auth.models import User, RolePermission


__all__ = ('AuthRepository',)


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
