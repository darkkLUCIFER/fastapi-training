from sqlalchemy.orm import Session

from src.core import BadRequestError, ConstraintViolation, IntegrityErrorTranslator
from src.todo.repository import TodoRepository
from src.core.database.uow import BaseUow
from src.todo.constants.constraint import PRIORITY_BETWEEN_CONSTRAINT


__all__ = ('TodoUow',)

TODO_INTEGRITY_ERRORS = IntegrityErrorTranslator(
    violations={
        PRIORITY_BETWEEN_CONSTRAINT: ConstraintViolation(BadRequestError, 'priority should between 1 AND 5'),
    },
)


class TodoUow(BaseUow):
    integrity_errors = TODO_INTEGRITY_ERRORS

    def __init__(self, session: Session):
        super().__init__(session)
        self.repository = TodoRepository(db=session)
