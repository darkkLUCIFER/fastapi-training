from src.todo.email import EmailService
from src.todo.services import TodoService
from src.todo.unit_of_work import TodoUnitOfWork


__all__ = ('get_todo_service',)


def get_todo_service() -> TodoService:
    return TodoService(TodoUnitOfWork(), EmailService())
