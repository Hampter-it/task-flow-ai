from collections.abc import Generator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from taskflow.database import get_db
from taskflow.main import app
from taskflow.models import Task


@pytest.fixture(autouse=True)
def assert_no_dependency_override_leaks() -> Generator[None, None, None]:
    """Check override cleanup after every test, including client-based ones."""
    yield
    assert app.dependency_overrides == {}


def test_health_through_client_with_database_override(
    client: TestClient,
) -> None:
    assert get_db in app.dependency_overrides

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_client_override_uses_session_bound_to_test_engine(
    client: TestClient,
    engine: Engine,
) -> None:
    override = app.dependency_overrides[get_db]
    dependency = override()
    session = next(dependency)

    try:
        assert session.get_bind() is engine
    finally:
        dependency.close()


def test_db_session_is_bound_to_test_engine(
    db_session: Session,
    engine: Engine,
) -> None:
    assert db_session.get_bind() is engine


def test_db_session_starts_with_empty_tasks_table(db_session: Session) -> None:
    assert db_session.scalar(select(func.count()).select_from(Task)) == 0


def test_task_committed_in_one_test_stays_in_its_own_fixture(
    db_session: Session,
) -> None:
    db_session.add(Task(title="Isolated task"))
    db_session.commit()

    assert db_session.scalar(select(func.count()).select_from(Task)) == 1


def test_committed_task_is_readable_through_fresh_session(
    session_factory: sessionmaker[Session],
) -> None:
    created_at = datetime(2026, 10, 31, 12, 0, 0)

    with session_factory() as writing_session:
        task = Task(
            title="Persisted task",
            description="Read it back",
            is_completed=True,
            created_at=created_at,
        )
        writing_session.add(task)
        writing_session.commit()
        task_id = task.id

    with session_factory() as reading_session:
        loaded = reading_session.get(Task, task_id)

    assert loaded is not None
    assert loaded.id == task_id
    assert loaded.title == "Persisted task"
    assert loaded.description == "Read it back"
    assert loaded.is_completed is True
    assert loaded.created_at == created_at


def test_no_tasks_routes_are_registered(client: TestClient) -> None:
    assert not any(
        path.startswith("/tasks") for path in app.openapi()["paths"]
    )
    assert client.get("/tasks").status_code == 404
