from sqlalchemy.orm import Session
from src.todo.models import Todo


__all__ = ('TodoRepository',)


class TodoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, todo: Todo) -> Todo:
        self.db.add(todo)
        return todo
