# Integration tests

Verify that real application components work together. Use an isolated test
database (SQLite or a dedicated disposable database), never the configured
development or production database. Cover real persistence, transaction
boundaries, repository queries, and service/repository collaboration.

Group tests under `auth/`, `todo/`, or `core/` according to the primary module
under test. Database and unit-of-work integration tests belong in `core/database/`.
