from types import TracebackType

import pytest
from sqlalchemy.orm import Session

from taskflow import database
from taskflow.config import settings


def test_engine_uses_configured_database_url() -> None:
    assert (
        database.engine.url.render_as_string(hide_password=False)
        == settings.database_url
    )


def test_session_factory_creates_configured_sessions() -> None:
    session = database.SessionLocal()

    try:
        assert isinstance(session, Session)
        assert session.get_bind() is database.engine
        assert session.autoflush is False
        assert session.expire_on_commit is False
    finally:
        session.close()


def test_get_db_yields_a_session_and_closes_it() -> None:
    dependency = database.get_db()
    session = next(dependency)

    try:
        assert isinstance(session, Session)
        assert session.get_bind() is database.engine
    finally:
        dependency.close()


class FakeSession:
    def __init__(self) -> None:
        self.closed = False

    def __enter__(self) -> "FakeSession":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        self.closed = True
        return False


def test_get_db_closes_session_when_consumer_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_session = FakeSession()
    monkeypatch.setattr(database, "SessionLocal", lambda: fake_session)

    dependency = database.get_db()
    assert next(dependency) is fake_session

    with pytest.raises(RuntimeError, match="boom"):
        dependency.throw(RuntimeError("boom"))

    assert fake_session.closed is True
