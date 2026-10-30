from unittest.mock import MagicMock

from src.todo.uow import TodoUow
from src.todo.services import TodoService
from src.todo.dependencies import get_todo_service


def test_todo_service_dependency_wires_session_and_email_service():
    session = MagicMock()

    service = get_todo_service(session)

    assert isinstance(service, TodoService)
    assert isinstance(service.uow, TodoUow)
    assert service.uow.session is session
    assert service.email is not None
