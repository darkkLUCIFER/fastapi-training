from contextlib import suppress, contextmanager

from src.core.database import session as database_session


def test_get_db_yields_session_and_closes_it(monkeypatch):
    class FakeSession:
        closed = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            self.closed = True

    fake_session = FakeSession()

    @contextmanager
    def session_context():
        with fake_session as session:
            yield session

    monkeypatch.setattr(database_session, 'SessionLocal', session_context)
    dependency = database_session.get_db()

    assert next(dependency) is fake_session
    with suppress(StopIteration):
        next(dependency)

    assert fake_session.closed is True
