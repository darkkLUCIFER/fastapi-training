# Books FastAPI

A FastAPI service with JWT authentication, role based permissions, and
user-owned todo items, plus a React frontend. The backend uses SQLAlchemy 2,
Alembic, and PostgreSQL (SQLite can be used for local tests).

## Quick start

Requirements: Python 3.12+, PostgreSQL, and Node.js/npm for the frontend.

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
# Edit .env and set DATABASE_URL and a private JWT_SECRET_KEY.
make migrate
make update_permissions
make create_super_user
make run_local_server
```

The API listens on `http://127.0.0.1:8001`. Interactive API documentation is
available at `/docs`, and the OpenAPI document is at `/openapi.json`.

Run the React frontend in another terminal:

```bash
cd frontend
npm install
npm run dev
```

## Documentation

- [Development setup and configuration](docs/development.md)
- [API endpoints and authentication](docs/api.md)
- [Architecture and data flow](docs/architecture.md)
- [Testing guide](docs/testing.md)

## Useful commands

Run from the repository root with the virtual environment activated:

| Command | Purpose |
| --- | --- |
| `make run_local_server` | Start the backend with reload on port 8001 |
| `make run_production_server` | Start the production ASGI server |
| `make makemigrations` | Create an Alembic migration (interactive message) |
| `make migrate` | Apply migrations to the configured database |
| `make downgrade` | Roll back one migration |
| `make current` / `make history` | Inspect migration state/history |
| `make create_super_user` | Interactively create an administrator |
| `make update_permissions` | Sync permission records and grants to the admin role |
| `./venv/bin/pytest -q` | Run backend tests |

Frontend checks run from `frontend/`: `npm test`, `npm run lint`, and
`npm run build`.
