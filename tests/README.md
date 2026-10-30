# Test organization

Tests are grouped first by **test purpose**, then by the application module they
exercise (`auth`, `todo`, `core`, or `utils`). Keep a test in the narrowest
category that accurately describes what it verifies.

## Categories

- `unit/`: isolated behavior; dependencies such as repositories or sessions may
  be mocked. No external service or real database is required.
- `integration/`: collaboration between real application components, especially
  SQLAlchemy sessions, repositories, units of work, and a dedicated test DB.
- `api/`: HTTP contract tests through FastAPI's `TestClient` or an async client.
  Override dependencies and isolate application state where appropriate.
- `architecture/`: cross-cutting structural rules such as dependency direction
  and model registration.
- `security/`: cross-cutting security guarantees such as sensitive-field
  protection, authentication, authorization, and ownership isolation.
- `smoke/`: minimal startup and critical operational-path checks. Keep these
  isolated from production resources.

## Module grouping

Use `auth/`, `todo/`, and `core/` under each category as relevant. Use `utils/`
for standalone project utilities that do not belong to an application module.
Shared fixtures belong in a category-level or root `conftest.py` only when
multiple tests genuinely share them; prefer local fixtures otherwise.

## Running tests

- Backend: `./venv/bin/pytest -q`
- Frontend API client: `cd frontend && npm test`
- Frontend static checks/build: `cd frontend && npm run lint && npm run build`

Module folders may contain a short `README.md` to document the intended scope
before the first test exists. Do not add empty test modules or placeholder test
functions just to fill a directory; keep test names descriptive of behavior.
