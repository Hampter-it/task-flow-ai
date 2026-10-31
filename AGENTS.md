Commands

- `uv sync` - install dependencies
- `uv run pytest` - the whole suite
- `uv run pytest tests/test_home.py` - one test file

Rules

- Dependencies are added in `pyproject.toml`. Do not add one without
  asking
- Adhere to clean code practices and SOLID principles by ensuring every class has a single responsibility, depends on abstractions rather than concrete implementations, and is open for extension but closed for modification.


Documents

- `_docs/process.md` - how work is organized
- `_docs/testing-guidelines.md` - how to write and run tests; read before writing tests
- `_docs/design-system.md` - UI tokens, components, states, and copy; read before any UI work
- `_docs/api.md` - the HTTP API contract; read before changing endpoints, schemas, or the typed client
- `_docs/plan.md` and `_docs/tasks.md` - the learning plan and the MVP backlog index
