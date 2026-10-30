from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError as DriverIntegrityError

from src.todo.uow import TodoUow
from src.core.exceptions import BadRequestError
from src.todo.repository import TodoRepository
from src.todo.constants.constraint import PRIORITY_BETWEEN_CONSTRAINT


def make_integrity_error(constraint_name=None):
    original = SimpleNamespace(pgcode=None, diag=SimpleNamespace(constraint_name=constraint_name))
    return DriverIntegrityError('statement', {}, original)


def test_initializes_repository_with_shared_session():
    session = MagicMock()

    uow = TodoUow(session)

    assert isinstance(uow.repository, TodoRepository)
    assert uow.repository.db is session


def test_commit_delegates_to_session():
    session = MagicMock()
    session.in_transaction.return_value = False
    uow = TodoUow(session)

    with uow:
        uow.commit()

    session.commit.assert_called_once_with()
    session.rollback.assert_not_called()


def test_priority_constraint_is_translated_and_failed_transaction_rolled_back():
    session = MagicMock()
    session.in_transaction.return_value = False
    session.commit.side_effect = make_integrity_error(PRIORITY_BETWEEN_CONSTRAINT)
    uow = TodoUow(session)

    with pytest.raises(BadRequestError, match='priority should between 1 AND 5'), uow:
        uow.commit()

    session.rollback.assert_called_once_with()


def test_unrecognized_constraint_uses_safe_fallback_error():
    session = MagicMock()
    session.in_transaction.return_value = False
    session.commit.side_effect = make_integrity_error('other_constraint')
    uow = TodoUow(session)

    with pytest.raises(BadRequestError, match='Invalid data'), uow:
        uow.commit()

    session.rollback.assert_called_once_with()
