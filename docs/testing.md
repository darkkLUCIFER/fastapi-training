# Testing guide

Backend tests use pytest and are grouped by the behavior they verify. The suite
is designed to run without connecting to the database configured in `.env`.

## Run the backend suite

From the repository root:

```bash
./venv/bin/pytest -q
```

Run one category or test module while iterating:

```bash
./venv/bin/pytest tests/unit/auth -q
./venv/bin/pytest tests/api -q
./venv/bin/pytest tests/integration -q
```

## Test categories

| Directory | What belongs there |
| --- | --- |
| `tests/unit/` | Isolated schemas, services, repositories, dependencies, and helpers |
| `tests/integration/` | Real components working together with an isolated database |
| `tests/api/` | HTTP status codes, request validation, authentication, and response contracts |
| `tests/architecture/` | Cross-module structural requirements such as model registration |
| `tests/security/` | Sensitive data exposure and other security guarantees |
| `tests/smoke/` | Application startup and essential operational paths |

Place module-specific tests under `auth/`, `todo/`, or `core/` where applicable.
Keep shared fixtures local unless multiple modules actually need them.

## Database isolation

Integration tests should create their own disposable SQLite database or use a
dedicated disposable test database. Never point a test at a developer's shared
database or a production database. The unit-of-work integration tests use an
in-memory SQLite engine and create/drop their own schema.

API tests use FastAPI's `TestClient` and dependency overrides to avoid external
services. Restore `app.dependency_overrides` after each test so one test cannot
change the behavior of another.

## Frontend checks

From `frontend/`:

```bash
npm install
npm test
npm run lint
npm run build
```

The API-client tests use Node's built-in test runner with mocked browser APIs
and `fetch`; they do not require a running backend. The lint command uses
Oxlint, and the build command runs Vite.
