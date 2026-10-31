# Development setup

This guide is for developers setting up and running the service locally.

## Requirements

- Python 3.12 or newer.
- PostgreSQL for a normal local environment. Unit and integration tests use
  isolated test data and do not need the configured database.
- Node.js and npm to run the React/Vite frontend.

## Install the backend

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
```

Set the values in `.env` before starting the application. `DATABASE_URL` must
point to a reachable database. For example:

```dotenv
DATABASE_URL=postgresql://app_user:app_password@localhost:5432/books
DEBUG=false
CORS_ORIGINS=["http://localhost:5173"]
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_REFRESH_ROTATION=true
JWT_TOKEN_LOCATION=Bearer
```

Generate a random secret with `openssl rand -hex 32`. Keep `.env` private and
use a different secret for each environment. `CORS_ORIGINS` is a JSON-style
list of allowed frontend origins. `JWT_TOKEN_LOCATION` configures the HTTP
authorization scheme; the default is `Bearer`.

The settings are loaded from `.env` by Pydantic Settings when `src.core.config`
is imported. SQLite URLs are accepted for local use and emit a warning because
PostgreSQL is the intended production database.

## Database setup and migrations

The application reads its SQLAlchemy URL from `DATABASE_URL`. Apply existing
migrations after configuring the database:

```bash
make migrate
```

After changing SQLAlchemy models, generate and inspect a migration:

```bash
make makemigrations
make migrate
```

Alembic imports `src.core.database.models` so every mapped model is registered
in `Base.metadata` for autogeneration. Review generated migrations before
applying them to shared or production databases. Use `make current` and
`make history` to inspect migration state. `make downgrade` rolls back one
revision.

## Initialize authorization data

After migrating a fresh database, run:

```bash
make update_permissions
make create_super_user
```

The first command creates missing permission rows from
`src/auth/constants/permission.py` and grants every declared permission to the
`admin` role. The second prompts for administrator credentials; passwords are
read without echoing them to the terminal.

## Run the services

Backend development server (port 8001):

```bash
make run_local_server
```

Production server:

```bash
make run_production_server
```

Frontend development server:

```bash
cd frontend
npm install
npm run dev
```

The frontend's API client uses `VITE_API_BASE` when provided and otherwise
uses same-origin requests. See `frontend/src/api.js` when changing the local
backend address.

## Troubleshooting

The project pins `passlib==1.7.4` with `bcrypt==4.3.0`. Keep these versions
compatible when changing password-hashing dependencies; newer bcrypt releases
have caused compatibility errors with this Passlib version. If password
hashing or verification starts failing after a dependency update, check the
installed versions against `pyproject.toml` first.

## Repository layout

| Path | Responsibility |
| --- | --- |
| `src/main.py` | FastAPI application, middleware, exception handlers, routers |
| `src/auth/` | Users, JWT authentication, roles, permissions, repositories and services |
| `src/todo/` | Todo API, validation, persistence and creation notification |
| `src/core/` | Settings, database base/session, unit of work, security and errors |
| `alembic/` | Database migration environment and revisions |
| `scripts/` | Administrator creation and permission synchronization |
| `frontend/` | React application and API client |
| `tests/` | Backend tests grouped by test purpose |
| `docs/` | Maintainer and API documentation |
