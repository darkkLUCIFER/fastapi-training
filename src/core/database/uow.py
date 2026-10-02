from types import TracebackType
from typing import Any, Self, ClassVar

from sqlalchemy.exc import IntegrityError as DriverIntegrityError
from sqlalchemy.orm import Session

from src.core.database.integrity import IntegrityErrorTranslator


__all__ = ('BaseUow',)


class BaseUow:
    """Unit of work: one repository, one session, one transaction.

    Committing is the only place a constraint violation can surface, so it is
    also the only place that needs to translate it. Subclasses opt in by setting
    ``integrity_errors``; units of work that leave it unset propagate the driver
    error untouched.
    """

    integrity_errors: ClassVar[IntegrityErrorTranslator | None] = None

    def __init__(self, session: Session):
        self.session = session

    def __enter__(self) -> Self:
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
        try:
            self.session.commit()
        except DriverIntegrityError as exc:
            # Roll back first: the session is unusable until the failed
            # transaction is closed, and the dependency may still be reused.
            self.rollback()
            if self.integrity_errors is None:
                raise
            raise self.integrity_errors(exc) from exc

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, obj: Any) -> None:
        self.session.refresh(obj)
