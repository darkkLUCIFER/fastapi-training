from src.todo.email import EmailService
from src.todo.services import TodoService
from src.todo.uow import TodoUow


__all__ = ('get_todo_service',)


def get_todo_service() -> TodoService:
    return TodoService(TodoUow(), EmailService())
