from types import TracebackType

from sqlalchemy.orm import Session

from src.auth.repository import AuthRepository


__all__ = ('AuthUow',)


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
