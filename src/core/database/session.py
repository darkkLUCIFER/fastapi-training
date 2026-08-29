from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import settings


__all__ = ('get_db', 'SessionLocal')

engine = create_engine(settings.database_url, echo=settings.debug)
SessionLocal = sessionmaker[Session](
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
