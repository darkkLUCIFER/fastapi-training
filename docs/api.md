# API reference

The running application publishes the complete OpenAPI schema at
`/openapi.json` and interactive Swagger UI at `/docs`.

All paths below include their trailing slash. Successful JSON responses are
validated by the route's Pydantic response model where one is declared.

## Authentication

| Method | Path | Access | Purpose |
| --- | --- | --- | --- |
| `POST` | `/auth/register/` | Public | Register a regular user |
| `POST` | `/auth/login/` | Public | Exchange username/password for access and refresh tokens |
| `POST` | `/auth/refresh/` | Public, refresh token in body | Issue a new access token and optionally rotate refresh token |
| `GET` | `/users/me/` | Access token | Return the current user's public identity |

Registration accepts JSON with `username`, `email`, `password`, and
`password_confirmation`. Usernames are trimmed, lowercased, and limited to
letters, digits, and underscores (3–100 characters). Passwords must be 8–50
characters. Login accepts `application/x-www-form-urlencoded` fields named
`username` and `password`.

Login and refresh return `access_token`, `refresh_token`, and `token_type`.
Send the access token on protected requests:

```http
Authorization: Bearer <access_token>
```

Refresh accepts JSON: `{"refresh_token": "<refresh_token>"}`. When
`JWT_REFRESH_ROTATION=true`, the old refresh token is revoked and a replacement
is returned. When rotation is disabled, the submitted refresh token is reused.
Inactive users cannot authenticate or refresh tokens.

## Todos

Every todo route requires an active authenticated user.

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/todo/` | Create a todo (201) |
| `GET` | `/todo/` | List todos visible to the current user |
| `GET` | `/todo/{todo_id}/` | Retrieve one todo |
| `PATCH` | `/todo/{todo_id}/` | Update supplied fields |
| `DELETE` | `/todo/{todo_id}/` | Delete one todo (204, empty body) |

Create accepts `title` (required, at least one character), optional
`description` (at least one character when supplied), and optional `priority`
(integer 1–5). Update accepts those fields plus `completed`; omitted fields
remain unchanged. Todo IDs must be positive integers.

Regular users only see and modify their own todos. Administrators can access all
todos. A missing todo and a todo owned by another regular user both produce the
application's not-found response.

## Permission administration

These routes require an active user with the corresponding permission key.

| Method | Path | Required permission |
| --- | --- | --- |
| `GET` | `/admin/permissions/` | `auth.permission.list.view` |
| `GET` | `/admin/role-permission/` | `auth.role-permission.list.view` |
| `POST` | `/admin/role-permission/create/` | `auth.role-permission.create` |
| `GET` | `/admin/role-permission/{role_permission_id}/` | `auth.role-permission.detail` |
| `PATCH` | `/admin/role-permission/{role_permission_id}/` | `auth.role-permission.update` (201 response) |
| `DELETE` | `/admin/role-permission/{role_permission_id}/` | `auth.role-permission.delete` |

The role-permission create body contains `role`, `permission_id`, and optional
`access` (defaults to `true`). Update accepts `role`, `permission_id`, and
`access`. Valid roles are `user` and `admin`.

## Common errors

| Status | Meaning |
| --- | --- |
| `400` | Invalid operation or duplicate registration |
| `401` | Missing, invalid, expired, or unsuitable token; inactive account |
| `403` | Authenticated user lacks the required permission |
| `404` | Resource not found or input values do not match |
| `409` | A known unique database constraint was violated |
| `422` | Request validation failed |

Error responses use a JSON `detail` field. FastAPI's standard validation
response for `422` contains structured validation details.
