# Testing guidelines

Read this before writing or changing tests. It applies to the FastAPI
backend and the React frontend.

## Principles

- Test behaviour, not implementation. A test should still pass if the
  internals are refactored without changing what the user or client sees.
- Every test must be deterministic and independent. It must not depend on
  another test, on execution order, or on a real network service.
- One test should have one reason to fail. If a test checks several
  unrelated things, split it.
- Every bug fix starts with a test that reproduces the bug.
- Tests are part of the task, not a follow-up. A feature without tests is
  not done.
- Do not add a test dependency without asking. `pytest`, `HTTPX`,
  `Vitest`, and the testing utilities included by the frontend scaffold
  are enough for the MVP.

## Test levels

| Level | Tool | What it covers | External services |
|---|---|---|---|
| Backend unit | pytest | Pure functions, validators, small helpers | None |
| API | pytest + FastAPI `TestClient` | Routes, status codes, validation, response bodies, persistence through the API | In-memory SQLite |
| Frontend API client | Vitest | URL and query construction, JSON handling, error mapping | Mocked `fetch` |
| Frontend component | Vitest + React Testing Library | What the user sees and does | Mocked API module |
| End-to-end | Not in the MVP | Full browser flows | PostgreSQL and both servers |

`TestClient` is built on HTTPX, so the API tests exercise the real
FastAPI request/response cycle without starting a server.

PostgreSQL integration tests and Playwright tests are deferred. Do not
add them to the MVP without an issue and an explicit dependency decision.

## Backend tests

### Layout and fixtures

- Put shared fixtures in `tests/conftest.py`, not in every test file.
- Use a function-scoped `client` fixture that:
  1. creates a fresh in-memory SQLite schema with `Base.metadata.create_all`;
  2. overrides the `get_db` dependency with a session bound to that engine;
  3. yields a `TestClient`;
  4. clears `app.dependency_overrides` and disposes the engine.
- Use `StaticPool` and `check_same_thread=False` for the in-memory
  SQLite engine so every session sees the same database.
- Create test data through the API unless the test is specifically about
  a lower layer. This keeps API tests black-box and catches serialization
  mistakes.
- Build payloads with a small helper such as
  `make_task_payload(**overrides)` instead of repeating dictionaries.
  Keep the helper explicit; do not hide important values behind a large
  factory library.

The application keeps PostgreSQL. SQLite is only a fast, isolated test
substitute. Do not write tests that depend on PostgreSQL-only behaviour
(such as specific collation or `timestamptz` semantics) until the
PostgreSQL integration suite exists.

### Required endpoint cases

Cover at least these cases for the task API:

- `GET /health`: returns `200` and `{"status": "ok"}`.
- `POST /tasks`:
  - valid title and description returns `201`;
  - the response has the full task shape and `is_completed` defaults to
    `false`;
  - an omitted description is returned as `null`;
  - a title of 1 character and a title of 200 characters are accepted;
  - an empty, whitespace-only, or 201-character title is rejected with
    `422`;
  - an explicitly created task can be read back.
- `GET /tasks`:
  - an empty database returns `[]`;
  - tasks are ordered by `id` ascending;
  - `is_completed=true` and `is_completed=false` return only matching
    tasks;
  - omitting the filter returns all tasks;
  - `offset` and `limit` paginate the filtered result;
  - `limit=1`, `limit=100`, and an offset past the end work;
  - `limit=0`, `limit=101`, and a negative offset return `422`;
  - filtering and pagination combined still apply the filter before the
    page is cut.
- `GET /tasks/{id}`:
  - an existing id returns `200` and the task;
  - a missing id returns `404` with `{"detail": "Task not found"}`;
  - a non-integer id returns `422`.
- `PATCH /tasks/{id}`:
  - updating only `is_completed` leaves the title and description alone;
  - updating only `title` leaves the other fields alone;
  - `description: null` clears the description;
  - `title: null` is rejected with `422`;
  - an empty body returns `200` and changes nothing;
  - a missing id returns `404`;
  - invalid field types return `422`.
- `DELETE /tasks/{id}`:
  - an existing task returns `204` with an empty body;
  - a subsequent `GET` returns `404`;
  - deleting the same task twice returns `404` the second time;
  - other tasks are untouched.

Also assert the API contract where it is cheap: the response is JSON, the
expected keys are present, and `created_at` parses as a date-time. Do not
assert the exact timestamp value.

### Backend rules

- Assert the status code and the behaviour that matters, not the whole
  response dictionary by default. Assert exact keys when the contract
  says the shape is fixed.
- Do not assert SQL, query counts, or ORM internals in endpoint tests.
- Do not mock the database in API tests. Use the real SQLAlchemy session
  against SQLite; that is the point of the fixture.
- Do not use `time.sleep`. If a timestamp matters, parse it and compare
  it with a range, or inject a clock through a dependency.
- Use `pytest.mark.parametrize` for input tables instead of copy-pasted
  tests.
- Use `caplog` only when logging is the behaviour under test. Do not
  assert on log strings as a proxy for application behaviour.
- Keep the suite fast. The backend suite should run on every commit.

## Frontend tests

### Boundaries

- Mock the API module (`src/api/tasks` or equivalent) in component tests.
  Components should not know about URLs, `fetch`, or HTTP details.
- Test the API client separately by stubbing `fetch`. Assert the URL,
  query string, method, headers, body, and error mapping.
- Do not hit a real backend in component tests. Do not rely on a running
  Vite proxy.
- If a test needs a router, query client, or provider, build a small
  `renderWithProviders` helper. Do not repeat provider setup in every
  test.

### Required component cases

- Task list: loading, success, empty, and error with retry.
- Filters: All, Active, and Completed each request the right filter and
  render the result; the empty-filter state offers a way back to All.
- Pagination: Previous and Next request the right offset; the controls
  are disabled at the boundaries.
- Create form: required-title validation, successful submit, server
  error keeps the form open with the entered values, and the submit
  button shows a pending state.
- Edit form: prefilled values, successful save, validation error, and
  server error.
- Completion toggle: the visible completed state changes after success,
  and a failed request does not leave the UI claiming success.
- Delete: the confirmation dialog appears, Cancel leaves the task,
  confirming removes it, and a failed delete shows an error.
- Accessibility: every interactive control has an accessible name; the
  main flows can be completed with the keyboard; a dialog returns focus
  to the control that opened it.

### Frontend rules

- Query by role, label, or visible text. Use `data-testid` only for an
  element that has no meaningful role or label.
- Prefer user-level interactions (`userEvent`) over calling component
  handlers directly. Use `fireEvent` only when the user-level utility
  cannot express the event.
- Await asynchronous UI with `findBy*` or `waitFor`. Never use arbitrary
  timeouts or sleeps.
- Reset mocks between tests and clean up the DOM after each test.
- Do not snapshot whole component trees. If a snapshot is truly useful,
  keep it small and explain why in the test.
- Do not assert Tailwind classes or exact CSS. Assert visible text,
  roles, accessible names, `aria-*` state, disabled state, and focus.
- Fix the clock (`vi.setSystemTime` or a fake timer) when a test renders
  a date. Do not write assertions that depend on the machine's timezone.
- Do not test third-party component internals. Test how the app uses
  them.
- Tests must not depend on network access, real timers, or a real
  browser extension.

## Test data and isolation

- Each test starts from a known empty state or creates exactly the data
  it needs.
- Do not share mutable fixtures between tests.
- Use realistic but non-sensitive values. Never use real credentials or
  production data.
- Do not commit `.env` values or secrets into tests.
- If a test needs a fixed date, build it explicitly, for example
  `datetime(2026, 10, 31, 12, 0, tzinfo=UTC)`.

## Naming and structure

- Backend: `tests/test_tasks.py` for task endpoints, `tests/test_health.py`
  for health. Name tests by behaviour: `test_create_task_rejects_blank_title`,
  not `test_post_endpoint_2`.
- Frontend: colocate tests next to components
  (`TaskList.test.tsx`) or under `src/__tests__` if the scaffold already
  uses that convention. Do not mix both.
- Use the arrange-act-assert shape. A short comment is fine when the
  setup is not obvious.
- A test name should say what happens and under which condition.

## Commands

Backend, from the repository root:

```bash
uv sync
uv run pytest
uv run pytest tests/test_tasks.py
uv run pytest tests/test_tasks.py::test_create_task_rejects_blank_title
uv run pytest -k "filter or pagination"
uv run pytest -x
```

Frontend, from `frontend/` once it is scaffolded:

```bash
npm test -- --run
```

The frontend scaffold must expose a `test` script that runs Vitest once
and exits non-zero on failure. If the project chooses another package
manager, update this document and `AGENTS.md` in the same change.

Manual Compose smoke testing is QA work, not a replacement for the
automated suites:

```bash
docker compose up --build
```

## Definition of done

A change is ready for QA when:

- New behaviour has tests at the appropriate level.
- The awkward cases in the acceptance criteria are covered, not just the
  happy path.
- The full backend suite passes with `uv run pytest`.
- The full frontend suite passes with the frontend test command.
- No test was skipped, marked `only`, or weakened to make the suite pass.
- A bug fix includes a regression test that fails without the fix.
- The issue or QA comment names the commands that were run and their
  result.

## Deliberately out of scope for the MVP

- A coverage percentage gate. Coverage is a signal, not the goal.
- PostgreSQL integration tests.
- Playwright or other browser end-to-end tests.
- Load, security, and mutation testing.
- Visual regression testing.

These can be added later through a task, but they must not be smuggled in
as part of an unrelated change.
