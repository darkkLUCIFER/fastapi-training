from fastapi import Depends
from sqlalchemy.orm import Session

from src.core.database.session import get_db
from src.todo.email import EmailService
from src.todo.services import TodoService
from src.todo.uow import TodoUow


__all__ = ("get_todo_service",)


def get_todo_service(db: Session = Depends(get_db)) -> TodoService:
    return TodoService(TodoUow(db), EmailService())
