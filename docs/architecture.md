# Architecture

The backend is organized around two application modules (`auth` and `todo`)
and shared infrastructure in `core`. FastAPI routers handle HTTP input and
dependency injection; services coordinate use cases; repositories contain
SQLAlchemy queries; unit-of-work objects coordinate a session and transaction.

## Request flow

For an authenticated todo request:

1. `src/main.py` includes the todo router under `/todo`.
2. `get_current_user` validates the bearer access token, loads the user, and
   rejects missing or inactive accounts.
3. `get_todo_service` builds a `TodoService` with a `TodoUow` and
   `EmailService` using the request's SQLAlchemy session.
4. `TodoService` applies the ownership rule and calls its repository.
5. The unit of work commits the transaction and rolls back unfinished work
   when its context exits.
6. FastAPI validates and serializes the response using the route's response
   schema.

## Modules

### Core

- `config.py` loads database, CORS, and JWT settings from environment variables
  and `.env`.
- `database/session.py` creates the SQLAlchemy engine and request-scoped
  `SessionLocal` dependency.
- `database/base.py` defines the declarative model base. Import every model in
  `database/models.py` so Alembic sees its metadata.
- `database/uow.py` provides `BaseUow`. Repositories stage changes; services
  decide when to commit. An unfinished transaction is rolled back on context
  exit. Integrity errors can be translated by module-specific unit-of-work
  subclasses.
- `services.py` contains password hashing and JWT creation, decoding, and
  refresh-token revocation.
- `exceptions.py` and `handlers.py` map application exceptions to HTTP
  responses. CORS middleware is configured in `middleware.py`.

### Authentication and authorization

`auth` contains the `User`, `Permission`, and `RolePermission` models, request
schemas, repositories, services, and routers. Access tokens identify the user
through the `sub` claim and include username and role claims. Refresh tokens
have a separate `type` claim and unique `jti`.

`get_current_payload` accepts the configured authorization scheme and requires
an access token. `get_current_user` then loads the user from the database and
checks that the account is active. Permission protected admin routes use
`RequirePermission`, which delegates the decision to `AuthorizationService`.
Permission keys are declared in `auth/constants/permission.py`; synchronize
them into the database with `make update_permissions`.

### Todos

`TodoService` owns todo use cases. Regular users can list, read, update, and
delete only their own records. Administrators can access records across users.
The repository exposes both unrestricted and owner-filtered queries; the
service chooses the appropriate query based on the authenticated user's role.

Creating a todo commits and refreshes the row before scheduling
`EmailService.send_created` as a FastAPI background task. The current email
service logs the creation event; it does not send an email to an external
provider.

## Transaction ownership

Use one unit-of-work context for a service operation. Repositories should not
commit independently. The service commits after all changes for the operation
are staged. If an exception occurs before commit, or the context exits with an
open transaction, `BaseUow` rolls it back. A read such as `refresh()` after a
commit can open another transaction, which the context manager also closes.

Subclasses can configure an `IntegrityErrorTranslator` to map known database
constraints to application exceptions. Unknown integrity errors continue to
propagate after rollback.

## Current operational limitations

- Refresh-token revocation is held in process memory. It is lost on restart and
  is not shared between multiple application workers; use shared storage for
  deployments that require durable revocation.
- The todo creation background task is a logging placeholder rather than an
  email delivery integration.
- The API currently has no logout endpoint or persisted refresh-token session
  table.
