from fastapi import BackgroundTasks

from src.todo.uow import TodoUow
from src.todo.email import EmailService
from src.auth.models import User
from src.todo.models import Todo
from src.todo.schema import CreateTodoSchema, UpdateTodoSchema
from src.auth.constants import RoleChoices
from src.core.exceptions import NotFoundError


__all__ = ('TodoService',)


class TodoService:
    def __init__(self, uow: TodoUow, email: EmailService):
        self.uow = uow
        self.email = email

    def _get_todo_or_raise(self, todo_id: int) -> Todo:
        todo = self.uow.repository.get_one(todo_id=todo_id)
        if not todo:
            raise NotFoundError(object_id=todo_id, model_name=Todo.__name__)
        return todo

    def create(self, data: CreateTodoSchema, background_tasks: BackgroundTasks, user: User) -> Todo:
        with self.uow:
            todo = Todo(**data.model_dump())
            todo.owner_id = user.id
            self.uow.repository.create(todo)
            self.uow.commit()
            self.uow.refresh(todo)
        background_tasks.add_task(self.email.send_created, todo)
        return todo

    def get_all(self, user) -> list[Todo]:
        if user.role == RoleChoices.ADMIN:
            return self.uow.repository.get_all()
        return self.uow.repository.get_all_user_todos(user_id=user.id)

    def get_one(self, todo_id: int) -> Todo:
        return self._get_todo_or_raise(todo_id)

    def update_one(self, todo_id: int, data: UpdateTodoSchema) -> Todo:
        with self.uow:
            todo = self._get_todo_or_raise(todo_id)
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(todo, field, value)
            self.uow.commit()
            self.uow.refresh(todo)
        return todo

    def delete_one(self, todo_id: int) -> None:
        with self.uow:
            todo = self._get_todo_or_raise(todo_id)
            self.uow.repository.delete(todo)
            self.uow.commit()
