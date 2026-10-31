# API contract

This document is the source of truth for the HTTP API the frontend builds
against. It defines routes, request and response shapes, status codes,
and error behaviour. If the code and this document disagree, resolve it
in the same task and update the document with the code.

The MVP API is single-user and has no authentication. The contract
covers the task CRUD flow, status filtering, and pagination.

## Conventions

- **Transport:** JSON over HTTP. Request bodies use
  `Content-Type: application/json`; responses are UTF-8 JSON unless the
  status is `204 No Content`.
- **Base URL:** `http://127.0.0.1:8000` when the API runs locally, and
  `http://localhost:8000` through Docker Compose.
- **Paths:** canonical paths have no trailing slash. Use `/tasks`, not
  `/tasks/`.
- **IDs:** positive integers assigned by the server. Clients treat them
  as opaque identifiers and do not assume they are contiguous.
- **Dates:** RFC 3339 / ISO 8601 timestamps in UTC. A `Z` suffix and a
  `+00:00` offset are both valid. Clients parse dates; they do not
  compare timestamp strings.
- **Booleans:** JSON `true` and `false`. Query parameters use `true` and
  `false`; do not depend on other spellings even if the framework accepts
  them.
- **Unknown request fields:** ignored in the MVP. A client cannot set
  server-owned fields such as `id` or `created_at` by sending them.
- **API version:** the MVP has no `/v1` path prefix. Treat the current
  contract as version 1. Additive changes are allowed; breaking changes
  follow the policy at the end of this document.

## Data model

A task is returned as a `TaskRead` object:

| Field | Type | Rules |
|---|---|---|
| `id` | integer | Server-assigned; read-only; positive |
| `title` | string | Required; 1–200 characters after trimming; never `null` |
| `description` | string or `null` | Optional; no maximum length in the MVP |
| `is_completed` | boolean | Defaults to `false`; set through `PATCH` |
| `created_at` | string (date-time) | Server-assigned when the task is created; read-only; UTC |

Example:

```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "description": "Practice the CRUD endpoints",
  "is_completed": false,
  "created_at": "2026-10-31T12:34:56Z"
}
```

`TaskCreate` accepts `title` and `description` only. `TaskUpdate` accepts
`title`, `description`, and `is_completed`, all optional. `TaskRead` is
the response shape and always contains every field above.

## Endpoint summary

| Method | Path | Operation ID | Success |
|---|---|---|---|
| `GET` | `/health` | `healthCheck` | `200` |
| `POST` | `/tasks` | `createTask` | `201` |
| `GET` | `/tasks` | `listTasks` | `200` |
| `GET` | `/tasks/{task_id}` | `getTask` | `200` |
| `PATCH` | `/tasks/{task_id}` | `updateTask` | `200` |
| `DELETE` | `/tasks/{task_id}` | `deleteTask` | `204` |

Set the operation IDs explicitly in FastAPI so generated clients do not
change when route names or tags change.

## Health

```http
GET /health
```

Returns `200 OK`:

```json
{"status": "ok"}
```

This is a liveness check for the API process. It does not query
PostgreSQL. A database readiness check is out of scope for the MVP.

## Create a task

```http
POST /tasks
Content-Type: application/json
```

Request body:

```json
{
  "title": "Learn FastAPI",
  "description": "Practice the CRUD endpoints"
}
```

Rules:

- `title` is required. It is trimmed of leading and trailing whitespace
  before validation and storage.
- A missing, `null`, empty, whitespace-only, or longer-than-200-character
  title is rejected with `422`.
- `description` may be omitted or set to `null`. An empty string is
  accepted and preserved; the UI sends `null` for a blank description.
- `is_completed` is not accepted on create. Every new task starts as
  `false`.
- `id` and `created_at` are assigned by the server.

Success: `201 Created` with the full `TaskRead` object:

```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "description": "Practice the CRUD endpoints",
  "is_completed": false,
  "created_at": "2026-10-31T12:34:56Z"
}
```

Errors: `422` for an invalid body.

## List tasks

```http
GET /tasks?is_completed=false&offset=0&limit=20
```

Query parameters:

| Parameter | Type | Default | Rules |
|---|---|---|---|
| `is_completed` | boolean | omitted | `true` returns completed tasks; `false` returns active tasks; omitted returns all |
| `offset` | integer | `0` | Greater than or equal to `0` |
| `limit` | integer | `20` | Between `1` and `100` inclusive |

Behaviour:

- Filtering is applied before pagination.
- Results are ordered by `id` ascending. The order is stable.
- The response is a bare JSON array, not an envelope.
- The MVP does not return a total count. The client may infer that
  another page might exist when the returned array has exactly `limit`
  items. An empty page is possible when the total is an exact multiple
  of `limit`.
- An `offset` past the end returns `200` with `[]`.
- An invalid filter value, `offset < 0`, `limit < 1`, or `limit > 100`
  returns `422`.

Example response:

```json
[
  {
    "id": 1,
    "title": "Learn FastAPI",
    "description": null,
    "is_completed": false,
    "created_at": "2026-10-31T12:34:56Z"
  },
  {
    "id": 2,
    "title": "Ship the MVP",
    "description": "Run the full Compose stack",
    "is_completed": true,
    "created_at": "2026-10-31T13:00:00Z"
  }
]
```

## Get a task

```http
GET /tasks/{task_id}
```

Path parameter:

| Parameter | Type | Rules |
|---|---|---|
| `task_id` | integer | A non-integer returns `422`; an integer with no matching task returns `404` |

Success: `200 OK` with the full `TaskRead` object.

Not found: `404 Not Found`:

```json
{"detail": "Task not found"}
```

## Update a task

```http
PATCH /tasks/{task_id}
Content-Type: application/json
```

`PATCH` is a partial update. Send only the fields that change:

```json
{"is_completed": true}
```

Rules:

- Omitted fields are left unchanged.
- `title` follows the same rules as create: 1–200 characters after
  trimming, never `null`. `title: null` returns `422`.
- `description: null` clears the description. Omitted `description` is
  left unchanged.
- `is_completed` must be a boolean. `is_completed: null` returns `422`.
- An empty object `{}` returns `200` and changes nothing.
- The update is atomic. If validation fails, no field is changed.
- There is no `PUT` endpoint in the MVP. Do not use `PATCH` to replace
  the whole object silently.

Success: `200 OK` with the updated `TaskRead` object.

Errors: `404` if the task does not exist; `422` for an invalid body.

Concurrency is last-write-wins in the MVP. There are no ETags or version
fields.

## Delete a task

```http
DELETE /tasks/{task_id}
```

Success: `204 No Content` with an empty body. The task is permanently
deleted; the MVP has no soft delete or restore.

Errors: `404 Not Found` if the task does not exist. Deleting the same
task twice returns `404` on the second request. Other tasks are not
affected.

## Errors

| Status | When | Body |
|---|---|---|
| `200` | Successful read or update | `TaskRead` or a list of tasks |
| `201` | Task created | `TaskRead` |
| `204` | Task deleted | Empty |
| `404` | Task not found | `{"detail": "Task not found"}` |
| `405` | Method not allowed on the path | Framework default |
| `422` | Invalid body, query parameter, or path parameter | FastAPI validation detail |
| `500` | Unhandled server error | Do not expose internals |

The `404` detail string is part of the contract and is exactly
`"Task not found"`.

A `422` response uses FastAPI/Pydantic's validation shape:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

Clients may use `loc` to map the error to a field. They must not depend
on the exact `msg` text; it can change with the validation library.
User-facing copy comes from the frontend, not from the server message.

`5xx` responses are not part of the success contract. The UI shows a
generic error and offers a retry.

## Browser access and CORS

The MVP serves the frontend and API through the same origin in Compose.
During local development, use a Vite proxy for `/tasks` and `/health`
pointing at `http://127.0.0.1:8000`. This avoids CORS and keeps the
frontend code origin-relative.

If direct cross-origin requests are unavoidable, allow only the explicit
development frontend origin. Do not use credentials; the MVP has no
cookies or authentication.

## OpenAPI and the typed client

The API exposes:

- `/openapi.json` — the machine-readable schema
- `/docs` — Swagger UI
- `/redoc` — ReDoc

The frontend's typed client is generated from `/openapi.json`. Generate
it from the running schema; do not hand-write request or response types
that duplicate the contract. When the schema changes, regenerate the
client in the same task.

Schema names are stable: `TaskCreate`, `TaskUpdate`, and `TaskRead`.
Operation IDs are the ones in the endpoint summary.

## Examples

Create a task:

```bash
curl -i -X POST http://localhost:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title": "Learn FastAPI"}'
```

List active tasks, first page:

```bash
curl -i 'http://localhost:8000/tasks?is_completed=false&offset=0&limit=20'
```

Complete a task:

```bash
curl -i -X PATCH http://localhost:8000/tasks/1 \
  -H 'Content-Type: application/json' \
  -d '{"is_completed": true}'
```

Delete a task:

```bash
curl -i -X DELETE http://localhost:8000/tasks/1
```

Health check:

```bash
curl -i http://localhost:8000/health
```

## Out of scope for the MVP

The following are deliberately absent. Do not add them without a task
and a contract update:

- authentication, users, and per-user ownership
- bulk operations
- search, configurable sorting, tags, priorities, and due dates
- soft delete, restore, and audit history
- ETags, optimistic concurrency, and conflict responses
- rate limiting and request quotas
- file attachments and imports/exports
- WebSockets and background jobs
- a pagination envelope with a total count
- an `updated_at` field
- a version prefix in the path
- internationalisation of API messages

Additive changes, such as a new optional response field, are allowed
when they do not break existing clients. Removing or renaming a field,
changing a type or default, or changing a status code is a breaking
change: introduce a new versioned path and migrate the client rather
than changing the contract silently.

## Change policy

- Update this document in the same task as any API change.
- Update or regenerate the typed client in the same task.
- Add endpoint tests following `_docs/testing-guidelines.md`.
- If an issue's acceptance criteria and this document disagree, raise
  it on the issue before implementing; do not guess.
