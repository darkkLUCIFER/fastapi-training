from types import TracebackType

from sqlalchemy.orm import Session

from src.todo.repository import TodoRepository


__all__ = ('TodoUow',)


class TodoUow:
    def __init__(self, session: Session):
        self.session = session
        self.repository = TodoRepository(db=session)

    def __enter__(self) -> 'TodoUow':
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
