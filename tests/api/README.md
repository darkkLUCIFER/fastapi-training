# API tests

Exercise externally observable HTTP behavior: status codes, response schemas,
validation, authentication/authorization, and error contracts. Group by the
router/module (`auth/`, `todo/`, `core/`). Use dependency overrides and isolated
state so tests do not depend on real external services.
