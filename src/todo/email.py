import logging

from src.todo.models import Todo


__all__ = ("EmailService",)

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send_created(todo: Todo) -> None:
        logger.info("Email -> todo %s created: %s", todo.id, todo.title)
