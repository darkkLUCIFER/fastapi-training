import pytest
from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker

from src.todo.uow import TodoUow
from src.auth.constants import RoleChoices
from src.todo.repository import TodoRepository
from src.core.database.base import Base
from src.core.database.models import Todo, User  # noqa: F401 — register all mapped tables


@pytest.fixture
def session_factory():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    try:
        yield factory
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


def create_user(session, user_id=1):
    user = User(id=user_id, username=f'user-{user_id}', hashed_password='test-hash', role=RoleChoices.USER)
    session.add(user)
    session.commit()
    return user


def test_real_unit_of_work_commit_persists_data(session_factory):
    with session_factory() as session:
        user = create_user(session)
        todo = TodoUow(session)
        with todo:
            todo.repository.create(Todo(owner_id=user.id, title='persist me'))
            todo.commit()

    with session_factory() as verification_session:
        assert verification_session.scalar(select(Todo.title)) == 'persist me'


def test_real_unit_of_work_rolls_back_uncommitted_changes(session_factory):
    with session_factory() as session:
        user = create_user(session)
        with TodoUow(session) as todo:
            todo.repository.create(Todo(owner_id=user.id, title='discard me'))

    with session_factory() as verification_session:
        assert verification_session.scalar(select(Todo.id)) is None


def test_real_unit_of_work_rolls_back_when_context_raises(session_factory):
    with session_factory() as session:
        user = create_user(session)
        with pytest.raises(RuntimeError, match='abort'), TodoUow(session) as todo:
            todo.repository.create(Todo(owner_id=user.id, title='discard me'))
            raise RuntimeError('abort')

    with session_factory() as verification_session:
        assert verification_session.scalar(select(Todo.id)) is None


def test_real_unit_of_work_closes_transaction_opened_by_read_after_commit(session_factory):
    with session_factory() as session:
        user = create_user(session)
        with TodoUow(session) as todo:
            record = Todo(owner_id=user.id, title='committed')
            todo.repository.create(record)
            todo.commit()
            todo.refresh(record)
            session.add(Todo(owner_id=user.id, title='uncommitted follow-up'))

    with session_factory() as verification_session:
        assert verification_session.scalars(select(Todo.title).order_by(Todo.id)).all() == ['committed']


def test_todo_repository_queries_real_rows_and_enforces_owner_filter(session_factory):
    with session_factory() as session:
        first_user = create_user(session, user_id=1)
        create_user(session, user_id=2)
        session.add_all(
            [
                Todo(owner_id=first_user.id, title='first user todo'),
                Todo(owner_id=2, title='second user todo'),
            ]
        )
        session.commit()

        repository = TodoRepository(session)

        assert [item.title for item in repository.get_all()] == ['first user todo', 'second user todo']
        assert [item.title for item in repository.get_all_user_todos(1)] == ['first user todo']
        assert repository.get_one_with_owner_check(2, 1) is None
        assert repository.get_one(2).title == 'second user todo'


def test_todo_repository_deletes_persisted_record(session_factory):
    with session_factory() as session:
        user = create_user(session)
        record = Todo(owner_id=user.id, title='remove me')
        session.add(record)
        session.commit()

        repository = TodoRepository(session)
        repository.delete(repository.get_one(record.id))
        session.commit()

        assert repository.get_one(record.id) is None
