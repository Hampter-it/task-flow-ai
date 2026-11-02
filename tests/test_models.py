from sqlalchemy import Boolean, DateTime, Integer, String, Text

from taskflow.database import Base
from taskflow.models import Task


def test_task_table_name() -> None:
    assert Task.__tablename__ == "tasks"


def test_task_registers_table_in_base_metadata() -> None:
    assert Base.metadata.tables == {"tasks": Task.__table__}


def test_task_has_exact_columns_in_order() -> None:
    assert list(Task.__table__.columns.keys()) == [
        "id",
        "title",
        "description",
        "is_completed",
        "created_at",
    ]
    assert set(Task.__table__.columns.keys()) == {
        "id",
        "title",
        "description",
        "is_completed",
        "created_at",
    }


def test_id_is_integer_primary_key() -> None:
    column = Task.__table__.c.id

    assert isinstance(column.type, Integer)
    assert column.primary_key is True
    assert column.nullable is False


def test_title_is_required_string_of_maximum_length_200() -> None:
    column = Task.__table__.c.title

    assert isinstance(column.type, String)
    assert column.type.length == 200
    assert column.nullable is False


def test_description_is_nullable_text() -> None:
    column = Task.__table__.c.description

    assert isinstance(column.type, Text)
    assert column.nullable is True


def test_is_completed_is_required_boolean_with_python_default_false() -> None:
    column = Task.__table__.c.is_completed

    assert isinstance(column.type, Boolean)
    assert column.nullable is False
    assert column.default is not None
    assert column.default.arg is False
    assert column.server_default is None


def test_created_at_is_required_timezone_datetime_with_server_default() -> None:
    column = Task.__table__.c.created_at

    assert isinstance(column.type, DateTime)
    assert column.type.timezone is True
    assert column.nullable is False
    assert column.default is None
    assert column.server_default is not None
    assert str(column.server_default.arg) == "now()"
