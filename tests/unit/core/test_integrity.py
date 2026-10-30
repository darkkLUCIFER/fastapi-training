from types import SimpleNamespace

import pytest
from sqlalchemy.exc import IntegrityError as DriverIntegrityError

from src.core.exceptions import ConflictError, BadRequestError
from src.core.database.integrity import (
    FALLBACK_VIOLATION,
    SQLSTATE_UNIQUE_VIOLATION,
    SQLSTATE_NOT_NULL_VIOLATION,
    SQLSTATE_FOREIGN_KEY_VIOLATION,
    ConstraintViolation,
    IntegrityErrorTranslator,
)


def make_integrity_error(pgcode=None, constraint_name=None):
    original = SimpleNamespace(pgcode=pgcode, diag=SimpleNamespace(constraint_name=constraint_name))
    return DriverIntegrityError('statement', {}, original)


@pytest.mark.parametrize(
    ('sqlstate', 'expected_type', 'detail'),
    [
        (SQLSTATE_UNIQUE_VIOLATION, ConflictError, 'Resource already exists'),
        (SQLSTATE_FOREIGN_KEY_VIOLATION, BadRequestError, 'Referenced resource does not exist'),
        (SQLSTATE_NOT_NULL_VIOLATION, BadRequestError, 'Missing required field'),
    ],
)
def test_translates_standard_postgres_sqlstates(sqlstate, expected_type, detail):
    translated = IntegrityErrorTranslator()(make_integrity_error(pgcode=sqlstate))

    assert isinstance(translated, expected_type)
    assert str(translated) == detail


def test_named_constraint_takes_precedence_over_sqlstate():
    translator = IntegrityErrorTranslator(
        violations={'uq_username': ConstraintViolation(ConflictError, 'username already exists')}
    )

    translated = translator(make_integrity_error(SQLSTATE_NOT_NULL_VIOLATION, 'uq_username'))

    assert isinstance(translated, ConflictError)
    assert str(translated) == 'username already exists'


def test_unknown_sqlstate_uses_fallback_without_exposing_driver_message():
    translated = IntegrityErrorTranslator()(make_integrity_error('99999'))

    assert isinstance(translated, FALLBACK_VIOLATION.error)
    assert str(translated) == FALLBACK_VIOLATION.detail


def test_custom_fallback_is_supported():
    translator = IntegrityErrorTranslator(fallback=ConstraintViolation(ConflictError, 'custom fallback'))

    assert str(translator(make_integrity_error())) == 'custom fallback'
