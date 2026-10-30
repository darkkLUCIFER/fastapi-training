from src.core.database import models  # noqa: F401 — import registers application models
from src.core.database.base import Base


def test_all_application_models_are_registered_for_migrations():
    assert {'users', 'permissions', 'role_permissions', 'todos'} <= set(Base.metadata.tables)


def test_database_tables_declare_primary_keys():
    for table in Base.metadata.sorted_tables:
        assert table.primary_key.columns, f'{table.name} has no primary key'
