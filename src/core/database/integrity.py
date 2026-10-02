from dataclasses import dataclass
from collections.abc import Mapping

from sqlalchemy.exc import IntegrityError as DriverIntegrityError

from src.core.exceptions import ConflictError, BadRequestError


__all__ = ('ConstraintViolation', 'IntegrityErrorTranslator')


@dataclass(frozen=True, slots=True)
class ConstraintViolation:
    """The domain error an API should raise for one violated constraint."""

    error: type[Exception]
    detail: str


# SQLSTATE codes, the portable way to classify a constraint violation.
SQLSTATE_UNIQUE_VIOLATION = '23505'
SQLSTATE_FOREIGN_KEY_VIOLATION = '23503'
SQLSTATE_NOT_NULL_VIOLATION = '23502'

DEFAULT_VIOLATIONS: Mapping[str, ConstraintViolation] = {
    SQLSTATE_UNIQUE_VIOLATION: ConstraintViolation(ConflictError, 'Resource already exists'),
    SQLSTATE_FOREIGN_KEY_VIOLATION: ConstraintViolation(BadRequestError, 'Referenced resource does not exist'),
    SQLSTATE_NOT_NULL_VIOLATION: ConstraintViolation(BadRequestError, 'Missing required field'),
}
FALLBACK_VIOLATION = ConstraintViolation(BadRequestError, 'Invalid data')


def _sqlstate(exc: DriverIntegrityError) -> str | None:
    return getattr(exc.orig, 'pgcode', None)


def _constraint_name(exc: DriverIntegrityError) -> str | None:
    return getattr(getattr(exc.orig, 'diag', None), 'constraint_name', None)


class IntegrityErrorTranslator:
    """Translate database constraint violations into domain exceptions.

    A unit of work declares the constraints its writes can trip so the API can
    report them precisely, e.g. a unique constraint becoming a 409 instead of an
    opaque 500. Anything left undeclared is classified by SQLSTATE, and anything
    the driver cannot classify falls back to a generic error, so driver
    internals never reach API clients.

    Resolution order: declared constraint name, then SQLSTATE, then fallback.
    """

    def __init__(
        self,
        violations: Mapping[str, ConstraintViolation] | None = None,
        fallback: ConstraintViolation | None = None,
    ):
        self._violations = dict(violations or {})
        self._fallback = fallback or FALLBACK_VIOLATION

    def __call__(self, exc: DriverIntegrityError) -> Exception:
        violation = self._resolve(exc)
        return violation.error(violation.detail)

    def _resolve(self, exc: DriverIntegrityError) -> ConstraintViolation:
        declared = self._violations.get(_constraint_name(exc))
        if declared is not None:
            return declared
        return DEFAULT_VIOLATIONS.get(_sqlstate(exc), self._fallback)
