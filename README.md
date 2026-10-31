# TaskFlow

TaskFlow is a FastAPI backend project managed with [uv](https://docs.astral.sh/uv/).

## Prerequisites

- Python 3.13
- uv
- Docker with Docker Compose v2 (for PostgreSQL)

## Setup

Install the project and its dependencies:

```bash
uv sync
```

Run the test suite:

```bash
uv run pytest
```

## Run the API

Start the development server:

```bash
uv run uvicorn taskflow.main:app --reload
```

Check the health endpoint:

```bash
curl -i http://127.0.0.1:8000/health
```

It returns `200 OK` with `Content-Type: application/json` and the body
`{"status": "ok"}`. This is a liveness check for the API process only.

## PostgreSQL

Start the database:

```bash
docker compose up -d db
```

Check that the service is running and healthy:

```bash
docker compose ps
```

`db` should be running with health status `healthy`. View the database logs:

```bash
docker compose logs db
```

Connect with a host `psql` client:

```bash
psql "postgresql://taskflow:taskflow_dev@localhost:5432/taskflow" \
  -c "SELECT current_database(), current_user;"
```

If `psql` is not installed on the host, use the in-container client instead:

```bash
docker compose exec db psql -U taskflow -d taskflow \
  -c "SELECT current_database(), current_user;"
```

The local development database is `taskflow`, with user `taskflow` and
password `taskflow_dev`. These credentials are for local development only;
never use them in production.

Stop the database:

```bash
docker compose down
```

`docker compose down` keeps the named `postgres_data` volume. Running
`docker compose down -v` **deletes the database data** because `-v` removes
the volume.

The API is not connected to PostgreSQL yet, and `/health` does not query
the database.
