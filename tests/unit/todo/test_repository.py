from unittest.mock import MagicMock

from src.todo.models import Todo
from src.todo.repository import TodoRepository


def test_create_adds_and_returns_todo():
    session = MagicMock()
    repository = TodoRepository(session)
    todo = Todo(title='Read', owner_id=1)

    assert repository.create(todo) is todo
    session.add.assert_called_once_with(todo)


def test_get_all_queries_todo_model():
    session = MagicMock()
    repository = TodoRepository(session)

    repository.get_all()

    session.query.assert_called_once_with(Todo)
    session.query.return_value.all.assert_called_once_with()


def test_get_one_filters_by_id():
    session = MagicMock()
    repository = TodoRepository(session)
    query = session.query.return_value

    repository.get_one(12)

    query.filter.assert_called_once()
    query.filter.return_value.first.assert_called_once_with()


def test_get_one_with_owner_check_filters_by_id_and_owner():
    session = MagicMock()
    repository = TodoRepository(session)
    query = session.query.return_value

    repository.get_one_with_owner_check(12, 4)

    query.filter.assert_called_once()
    assert len(query.filter.call_args.args) == 2
    query.filter.return_value.first.assert_called_once_with()


def test_get_all_user_todos_filters_by_owner():
    session = MagicMock()
    repository = TodoRepository(session)
    query = session.query.return_value

    repository.get_all_user_todos(4)

    query.filter.assert_called_once()
    query.filter.return_value.all.assert_called_once_with()


def test_delete_delegates_to_session():
    session = MagicMock()
    repository = TodoRepository(session)
    todo = Todo(title='Read', owner_id=1)

    repository.delete(todo)

    session.delete.assert_called_once_with(todo)
