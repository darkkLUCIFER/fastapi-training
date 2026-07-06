from fastapi import BackgroundTasks

from src.core.exceptions import NotFoundError
from src.todo.email import EmailService
from src.todo.models import Todo
from src.todo.schema import CreateTodoSchema, UpdateTodoSchema
from src.todo.uow import TodoUow


__all__ = ('TodoService',)


class TodoService:
    def __init__(self, uow: TodoUow, email: EmailService):
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

    def get_all(self) -> list[Todo]:
        with self.uow:
            return self.uow.repository.get_all()

    def get_one(self, todo_id: int) -> Todo:
        with self.uow:
            todo = self.uow.repository.get_one(todo_id=todo_id)
            if not todo:
                raise NotFoundError(object_id=todo_id, model_name=Todo.__name__)
            return todo

    def update_one(self, todo_id: int, data: UpdateTodoSchema) -> Todo:
        with self.uow:
            todo = self.uow.repository.get_one(todo_id=todo_id)
            if not todo:
                raise NotFoundError(object_id=todo_id, model_name=Todo.__name__)
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(todo, field, value)
            self.uow.repository.update(todo)
            self.uow.commit()
            self.uow.refresh(todo)
            return todo

    def delete_one(self, todo_id: int) -> None:
        with self.uow:
            todo = self.uow.repository.get_one(todo_id=todo_id)
            if not todo:
                raise NotFoundError(object_id=todo_id, model_name=Todo.__name__)
            self.uow.repository.delete(todo)
            self.uow.commit()
