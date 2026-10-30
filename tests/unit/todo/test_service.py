from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import BackgroundTasks

from src.todo.models import Todo
from src.todo.schema import CreateTodoSchema, UpdateTodoSchema
from src.todo.services import TodoService
from src.auth.constants import RoleChoices
from src.core.exceptions import NotFoundError


@pytest.fixture
def collaborators():
    uow = MagicMock()
    uow.__enter__.return_value = uow
    uow.__exit__.return_value = None
    email = MagicMock()
    return uow, email, TodoService(uow, email)


def user(user_id=7, role=RoleChoices.USER):
    return SimpleNamespace(id=user_id, role=role)


def todo(todo_id=11, owner_id=7):
    return Todo(id=todo_id, owner_id=owner_id, title='Original', description='Details', priority=2, completed=False)


def test_create_persists_refreshes_and_schedules_created_email(collaborators):
    uow, email, service = collaborators
    uow.repository.create.side_effect = lambda item: setattr(item, 'id', 11)
    tasks = BackgroundTasks()

    result = service.create(CreateTodoSchema(title='New', priority=3), tasks, user())

    assert result.title == 'New'
    assert result.owner_id == 7
    uow.repository.create.assert_called_once_with(result)
    uow.commit.assert_called_once_with()
    uow.refresh.assert_called_once_with(result)
    assert len(tasks.tasks) == 1
    assert tasks.tasks[0].func == email.send_created
    assert tasks.tasks[0].args == (result,)


def test_get_all_limits_regular_users_to_their_todos(collaborators):
    uow, _, service = collaborators

    service.get_all(user(7))

    uow.repository.get_all_user_todos.assert_called_once_with(user_id=7)
    uow.repository.get_all.assert_not_called()


def test_get_all_returns_all_todos_for_admin(collaborators):
    uow, _, service = collaborators

    service.get_all(user(role=RoleChoices.ADMIN))

    uow.repository.get_all.assert_called_once_with()
    uow.repository.get_all_user_todos.assert_not_called()


def test_get_one_enforces_owner_for_regular_user(collaborators):
    uow, _, service = collaborators
    expected = todo()
    uow.repository.get_one_with_owner_check.return_value = expected

    assert service.get_one(11, user()) is expected
    uow.repository.get_one_with_owner_check.assert_called_once_with(todo_id=11, user_id=7)
    uow.repository.get_one.assert_not_called()


def test_admin_get_one_does_not_apply_owner_filter(collaborators):
    uow, _, service = collaborators
    expected = todo(owner_id=99)
    uow.repository.get_one.return_value = expected

    assert service.get_one(11, user(role=RoleChoices.ADMIN)) is expected
    uow.repository.get_one.assert_called_once_with(todo_id=11)
    uow.repository.get_one_with_owner_check.assert_not_called()


def test_get_one_raises_not_found_for_missing_or_foreign_todo(collaborators):
    uow, _, service = collaborators
    uow.repository.get_one_with_owner_check.return_value = None

    with pytest.raises(NotFoundError) as error:
        service.get_one(11, user())

    assert error.value.object_id == 11
    assert error.value.model_name == 'Todo'


def test_update_applies_only_supplied_fields_and_commits(collaborators):
    uow, _, service = collaborators
    existing = todo()
    uow.repository.get_one_with_owner_check.return_value = existing

    result = service.update_one(11, UpdateTodoSchema(title='Changed', completed=True), user())

    assert result is existing
    assert (result.title, result.description, result.priority, result.completed) == ('Changed', 'Details', 2, True)
    uow.commit.assert_called_once_with()
    uow.refresh.assert_called_once_with(existing)


def test_update_allows_admin_to_update_another_users_todo(collaborators):
    uow, _, service = collaborators
    existing = todo(owner_id=99)
    uow.repository.get_one.return_value = existing

    service.update_one(11, UpdateTodoSchema(priority=5), user(role=RoleChoices.ADMIN))

    assert existing.priority == 5
    uow.repository.get_one.assert_called_once_with(todo_id=11)


def test_update_missing_todo_raises_and_does_not_commit(collaborators):
    uow, _, service = collaborators
    uow.repository.get_one_with_owner_check.return_value = None

    with pytest.raises(NotFoundError):
        service.update_one(11, UpdateTodoSchema(title='Changed'), user())

    uow.commit.assert_not_called()


def test_delete_removes_owned_todo_and_commits(collaborators):
    uow, _, service = collaborators
    existing = todo()
    uow.repository.get_one_with_owner_check.return_value = existing

    assert service.delete_one(11, user()) is None

    uow.repository.delete.assert_called_once_with(existing)
    uow.commit.assert_called_once_with()


def test_admin_can_delete_another_users_todo(collaborators):
    uow, _, service = collaborators
    existing = todo(owner_id=99)
    uow.repository.get_one.return_value = existing

    service.delete_one(11, user(role=RoleChoices.ADMIN))

    uow.repository.delete.assert_called_once_with(existing)


def test_delete_missing_or_foreign_todo_raises_without_deleting(collaborators):
    uow, _, service = collaborators
    uow.repository.get_one_with_owner_check.return_value = None

    with pytest.raises(NotFoundError):
        service.delete_one(11, user())

    uow.repository.delete.assert_not_called()
    uow.commit.assert_not_called()
