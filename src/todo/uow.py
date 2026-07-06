from types import TracebackType

from sqlalchemy.orm import Session

from src.core import SessionLocal
from src.todo.repository import TodoRepository


__all__ = ("TodoUow",)


class TodoUow:
    def __init__(self, session_factory=SessionLocal):
        self._session_factory = session_factory

    def __enter__(self) -> "TodoUow":
        self.session: Session = self._session_factory()
        self.repository = TodoRepository(db=self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()
        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, obj) -> None:
        self.session.refresh(obj)
