# Unit tests

Test one unit of behavior in isolation. Mock external collaborators where
appropriate; these tests should be fast and deterministic.

- `auth/`: authentication, authorization, permission, schema, and repository behavior.
- `todo/`: todo schema, service, repository, and notification behavior.
- `core/`: security utilities, configuration, exception translation, and core helpers.
- `core/database/`: unit-level database infrastructure logic (mocked sessions).
- `scripts/`: safe tests for standalone management command behavior.
- `utils/`: standalone project utility scripts and helpers.
