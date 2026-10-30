from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.todo.schema import CreateTodoSchema, UpdateTodoSchema, TodoResponseSchema


@pytest.mark.parametrize('payload', [{'title': ''}, {'title': None}, {}])
def test_create_schema_requires_non_empty_title(payload):
    with pytest.raises(ValidationError):
        CreateTodoSchema.model_validate(payload)


@pytest.mark.parametrize('priority', [0, 6, -1])
def test_create_schema_rejects_priority_outside_range(priority):
    with pytest.raises(ValidationError):
        CreateTodoSchema(title='Read', priority=priority)


def test_create_schema_accepts_optional_fields_and_valid_priority():
    todo = CreateTodoSchema(title='Read', description='A book', priority=5)

    assert todo.model_dump() == {'title': 'Read', 'description': 'A book', 'priority': 5}
    assert CreateTodoSchema(title='Read').description is None


@pytest.mark.parametrize('field,value', [('title', ''), ('description', ''), ('priority', 0), ('priority', 6)])
def test_update_schema_validates_supplied_fields(field, value):
    with pytest.raises(ValidationError):
        UpdateTodoSchema.model_validate({field: value})


def test_update_schema_preserves_partial_update_fields_and_explicit_null():
    update = UpdateTodoSchema(description=None, completed=True)

    assert update.model_dump(exclude_unset=True) == {'description': None, 'completed': True}


def test_response_schema_reads_attributes():
    now = datetime.now(UTC)
    todo = TodoResponseSchema.model_validate(
        SimpleTodo(id=1, title='Read', description=None, priority=2, completed=False, created_at=now, updated_at=now)
    )

    assert todo.id == 1
    assert todo.created_at == now


class SimpleTodo:
    def __init__(self, **values):
        self.__dict__.update(values)
