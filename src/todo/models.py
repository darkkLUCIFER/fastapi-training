from sqlalchemy import String, SmallInteger, CheckConstraint, false, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core import Base
from src.core.database.mixins import TimestampMixin


__all__ = ("Todo",)


class Todo(TimestampMixin, Base):
    __tablename__ = "todos"
    __table_args__ = (
        CheckConstraint(
            "priority BETWEEN 1 AND 5",
            name="ck_todos_priority",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(length=100))
    description: Mapped[str | None] = mapped_column(String(length=500))
    priority: Mapped[int | None] = mapped_column(SmallInteger)
    completed: Mapped[bool] = mapped_column(default=False, server_default=false())
