from types import TracebackType

from sqlalchemy.orm import Session

from src.auth.repository import AuthRepository, PermissionRepository, RolePermissionRepository


__all__ = ('AuthUow', 'PermissionUow', 'RolePermissionUow')


class AuthUow:
    def __init__(self, session: Session):
        self.session = session
        self.repository = AuthRepository(db=session)

    def __enter__(self) -> 'AuthUow':
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, obj) -> None:
        self.session.refresh(obj)


class RolePermissionUow:
    def __init__(self, session: Session):
        self.session = session
        self.repository = RolePermissionRepository(db=session)

    def __enter__(self) -> 'RolePermissionUow':
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, obj) -> None:
        self.session.refresh(obj)


class PermissionUow:
    def __init__(self, session: Session):
        self.session = session
        self.repository = PermissionRepository(db=session)

    def __enter__(self) -> 'PermissionUow':
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, obj) -> None:
        self.session.refresh(obj)
