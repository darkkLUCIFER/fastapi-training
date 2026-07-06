from sqlalchemy.orm import Session
from src.todo.models import Todo


__all__ = ('TodoRepository',)


class TodoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, todo: Todo) -> Todo:
        self.db.add(todo)
        return todo

    def get_all(self) -> list[Todo]:
        return self.db.query(Todo).all()  # noqa

    def get_one(self, todo_id: int) -> Todo | None:
        return self.db.query(Todo).filter(Todo.id == todo_id).first()

    def update(self, todo: Todo) -> Todo:
        self.db.merge(todo)
        return todo
