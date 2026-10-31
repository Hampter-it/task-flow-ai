# TaskFlow MVP backlog

The MVP is a single-user web app for creating, viewing, editing, completing, deleting, and filtering tasks. It uses Python 3.13, FastAPI, PostgreSQL 17, SQLAlchemy 2.0 (sync), Alembic, Pydantic v2, uv, Docker Compose, pytest/HTTPX; React, TypeScript, Vite, TanStack Query, React Hook Form, Zod, Tailwind CSS, shadcn/ui, and Vitest.

The task details now live in GitHub issues. This file is an index of the MVP backlog:

| # | Task |
|---|---|
| 1 | [#1 — Scaffold an empty project with a passing test](https://github.com/Hampter-it/task-flow-ai/issues/1) |
| 2 | [#2 — Add the health endpoint and PostgreSQL via Docker Compose](https://github.com/Hampter-it/task-flow-ai/issues/2) |
| 3 | [#3 — Add settings and a SQLAlchemy session dependency](https://github.com/Hampter-it/task-flow-ai/issues/3) |
| 4 | [#4 — Add the Task model and initial Alembic migration](https://github.com/Hampter-it/task-flow-ai/issues/4) |
| 5 | [#5 — Add Pydantic schemas and isolated database test fixtures](https://github.com/Hampter-it/task-flow-ai/issues/5) |
| 6 | [#6 — Add the create-task endpoint](https://github.com/Hampter-it/task-flow-ai/issues/6) |
| 7 | [#7 — Add the list-tasks endpoint with pagination and status filtering](https://github.com/Hampter-it/task-flow-ai/issues/7) |
| 8 | [#8 — Add the get, update, and delete endpoints](https://github.com/Hampter-it/task-flow-ai/issues/8) |
| 9 | [#9 — Add a Dockerfile for the API](https://github.com/Hampter-it/task-flow-ai/issues/9) |
| 10 | [#10 — Add the API service to Compose and verify persistence](https://github.com/Hampter-it/task-flow-ai/issues/10) |
| 11 | [#11 — Define the frontend design system](https://github.com/Hampter-it/task-flow-ai/issues/11) |
| 12 | [#12 — Scaffold the React frontend with Tailwind, shadcn/ui, and a passing test](https://github.com/Hampter-it/task-flow-ai/issues/12) |
| 13 | [#13 — Generate a typed API client and build the task list page](https://github.com/Hampter-it/task-flow-ai/issues/13) |
| 14 | [#14 — Add status filtering and pagination controls to the task list](https://github.com/Hampter-it/task-flow-ai/issues/14) |
| 15 | [#15 — Add the create-task form](https://github.com/Hampter-it/task-flow-ai/issues/15) |
| 16 | [#16 — Add edit and completion toggle to the UI](https://github.com/Hampter-it/task-flow-ai/issues/16) |
| 17 | [#17 — Add delete with confirmation to the UI](https://github.com/Hampter-it/task-flow-ai/issues/17) |
| 18 | [#18 — Containerize the frontend and serve the full MVP through Compose](https://github.com/Hampter-it/task-flow-ai/issues/18) |

The MVP is complete when `docker compose up --build` serves the React UI, the UI can exercise every task flow, and both test suites pass.

Not in this MVP: authentication and users, a service layer, CI, PostgreSQL integration tests, Playwright end-to-end tests, multi-page routing, production deployment, and observability. These are deferred until after the first working version.
