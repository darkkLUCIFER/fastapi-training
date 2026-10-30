import asyncio
import logging

from src.todo.email import EmailService
from src.todo.models import Todo


def test_send_created_logs_todo_details(caplog):
    todo = Todo(id=8, title='Read a book', owner_id=2)

    with caplog.at_level(logging.INFO, logger='src.todo.email'):
        assert asyncio.run(EmailService.send_created(todo)) is None

    assert 'Email -> todo 8 created: Read a book' in caplog.text
