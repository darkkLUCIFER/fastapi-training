from types import TracebackType
from typing import Any, Self, ClassVar

from sqlalchemy.exc import IntegrityError as DriverIntegrityError
from sqlalchemy.orm import Session

from src.core.database.integrity import IntegrityErrorTranslator


__all__ = ('BaseUow',)


class BaseUow:
    """Unit of work: coordinate repositories on one session and transaction.

    Repositories stage changes without committing. The service commits once the
    operation is ready; an uncommitted transaction is rolled back on context exit.
    Committing is also where constraint violations are translated. Subclasses opt
    in by setting ``integrity_errors``; otherwise driver errors propagate.
    """

    integrity_errors: ClassVar[IntegrityErrorTranslator | None] = None

    def __init__(self, session: Session):
        self.session = session
        self._transaction_finished = False

    def __enter__(self) -> Self:
        self._transaction_finished = False
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        # A read after commit (for example, refresh) can open another transaction.
        # Close it too, and discard any work if the context exits without a commit.
        if not self._transaction_finished or self.session.in_transaction():
            self.rollback()

    def commit(self) -> None:
        try:
            self.session.commit()
            self._transaction_finished = True
        except DriverIntegrityError as exc:
            # Roll back first: the session is unusable until the failed
            # transaction is closed, and the dependency may still be reused.
            self.rollback()
            if self.integrity_errors is None:
                raise
            raise self.integrity_errors(exc) from exc

    def rollback(self) -> None:
        self.session.rollback()
        self._transaction_finished = True

    def refresh(self, obj: Any) -> None:
        self.session.refresh(obj)
