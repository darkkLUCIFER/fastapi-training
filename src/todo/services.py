from fastapi import BackgroundTasks

from src.todo.email import EmailService
from src.todo.models import Todo
from src.todo.schema import CreateTodoSchema
from src.todo.unit_of_work import TodoUnitOfWork


__all__ = ('TodoService',)


class TodoService:
    def __init__(self, uow: TodoUnitOfWork, email: EmailService):
        self.uow = uow
        self.email = email

    def create(self, data: CreateTodoSchema, background_tasks: BackgroundTasks) -> Todo:
        todo = Todo(**data.model_dump())
        with self.uow:
            self.uow.repository.create(todo)
            self.uow.commit()
            self.uow.refresh(todo)
        background_tasks.add_task(self.email.send_created, todo)
        return todo
