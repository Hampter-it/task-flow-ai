from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from taskflow.models import Task
from taskflow.schemas import TaskCreate, TaskRead, TaskUpdate

VALID_TITLES = [
    pytest.param("a", "a", id="one-character"),
    pytest.param("x" * 200, "x" * 200, id="200-characters"),
    pytest.param(
        f"  {'x' * 200}  ",
        "x" * 200,
        id="200-characters-with-surrounding-whitespace",
    ),
]

INVALID_TITLES = [
    pytest.param(None, id="null"),
    pytest.param("", id="empty"),
    pytest.param(" \t\n ", id="whitespace-only"),
    pytest.param(123, id="non-string"),
    pytest.param("x" * 201, id="201-characters"),
    pytest.param(f"  {'x' * 201}  ", id="201-characters-with-surrounding-whitespace"),
]

TASK_READ_PAYLOAD = {
    "id": 1,
    "title": "Learn FastAPI",
    "description": None,
    "is_completed": False,
    "created_at": datetime(2026, 10, 31, 12, 0, tzinfo=UTC),
}


def assert_field_error(
    exc_info: pytest.ExceptionInfo[ValidationError],
    field: str,
) -> None:
    assert any(error["loc"] == (field,) for error in exc_info.value.errors())


def test_task_create_has_only_title_and_description() -> None:
    assert set(TaskCreate.model_fields) == {"title", "description"}


def test_task_update_has_title_description_and_is_completed() -> None:
    assert set(TaskUpdate.model_fields) == {
        "title",
        "description",
        "is_completed",
    }


def test_task_read_has_all_response_fields() -> None:
    assert set(TaskRead.model_fields) == {
        "id",
        "title",
        "description",
        "is_completed",
        "created_at",
    }


def test_task_create_trims_title_before_validation() -> None:
    task = TaskCreate(title="  Learn FastAPI  ")

    assert task.title == "Learn FastAPI"
    assert task.model_dump()["title"] == "Learn FastAPI"


@pytest.mark.parametrize(("title", "expected"), VALID_TITLES)
def test_task_create_accepts_titles_within_bounds(
    title: str,
    expected: str,
) -> None:
    task = TaskCreate(title=title)

    assert task.title == expected


@pytest.mark.parametrize("title", INVALID_TITLES)
def test_task_create_rejects_invalid_titles(title: object) -> None:
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(title=title)

    assert_field_error(exc_info, "title")


def test_task_create_rejects_missing_title() -> None:
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate()

    assert_field_error(exc_info, "title")


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        pytest.param({}, None, id="omitted"),
        pytest.param({"description": None}, None, id="null"),
        pytest.param({"description": ""}, "", id="empty"),
        pytest.param(
            {"description": "  keep these spaces  "},
            "  keep these spaces  ",
            id="non-empty-is-not-trimmed",
        ),
        pytest.param(
            {"description": "x" * 10_000},
            "x" * 10_000,
            id="10000-characters",
        ),
    ],
)
def test_task_create_handles_description(
    kwargs: dict[str, object],
    expected: str | None,
) -> None:
    task = TaskCreate(title="A title", **kwargs)

    assert task.description == expected
    assert task.model_dump()["description"] == expected


def test_task_update_allows_omitted_title() -> None:
    update = TaskUpdate()

    assert update.title is None
    assert "title" not in update.model_dump(exclude_unset=True)


def test_task_update_rejects_explicit_null_title() -> None:
    with pytest.raises(ValidationError) as exc_info:
        TaskUpdate(title=None)

    assert_field_error(exc_info, "title")


@pytest.mark.parametrize(("title", "expected"), VALID_TITLES)
def test_task_update_accepts_and_trims_valid_titles(
    title: str,
    expected: str,
) -> None:
    update = TaskUpdate(title=title)

    assert update.title == expected
    assert update.model_dump(exclude_unset=True) == {"title": expected}


@pytest.mark.parametrize("title", INVALID_TITLES)
def test_task_update_rejects_invalid_titles(title: object) -> None:
    with pytest.raises(ValidationError) as exc_info:
        TaskUpdate(title=title)

    assert_field_error(exc_info, "title")


def test_task_update_omits_unset_description() -> None:
    update = TaskUpdate()

    assert "description" not in update.model_dump(exclude_unset=True)


def test_task_update_preserves_null_description() -> None:
    update = TaskUpdate(description=None)

    assert update.model_dump(exclude_unset=True) == {"description": None}


def test_task_update_preserves_empty_description() -> None:
    update = TaskUpdate(description="")

    assert update.model_dump(exclude_unset=True) == {"description": ""}


def test_task_update_allows_omitted_is_completed() -> None:
    update = TaskUpdate()

    assert "is_completed" not in update.model_dump(exclude_unset=True)


@pytest.mark.parametrize("is_completed", [True, False])
def test_task_update_accepts_boolean_is_completed(is_completed: bool) -> None:
    update = TaskUpdate(is_completed=is_completed)

    assert update.model_dump(exclude_unset=True) == {
        "is_completed": is_completed,
    }


@pytest.mark.parametrize("is_completed", [None, "not-a-bool"])
def test_task_update_rejects_invalid_is_completed(is_completed: object) -> None:
    with pytest.raises(ValidationError) as exc_info:
        TaskUpdate(is_completed=is_completed)

    assert_field_error(exc_info, "is_completed")


def test_task_update_with_no_fields_is_valid_and_changes_nothing() -> None:
    update = TaskUpdate()

    assert update.model_dump(exclude_unset=True) == {}


def test_task_create_ignores_unknown_fields() -> None:
    task = TaskCreate(
        title="x",
        id=99,
        created_at="2026-01-01T00:00:00Z",
        is_completed=True,
    )

    assert task.model_dump() == {"title": "x", "description": None}
    assert "is_completed" not in TaskCreate.model_fields


def test_task_update_ignores_unknown_fields() -> None:
    update = TaskUpdate(
        is_completed=True,
        id=99,
        created_at="2026-01-01T00:00:00Z",
    )

    dumped = update.model_dump()

    assert "id" not in dumped
    assert "created_at" not in dumped
    assert set(dumped) == {"title", "description", "is_completed"}


@pytest.mark.parametrize("description", [None, "Practice the CRUD endpoints"])
def test_task_read_maps_all_fields_from_task_orm_instance(
    description: str | None,
) -> None:
    created_at = datetime(2026, 10, 31, 12, 34, 56, tzinfo=UTC)
    task = Task(
        id=7,
        title="Learn FastAPI",
        description=description,
        is_completed=True,
        created_at=created_at,
    )

    read = TaskRead.model_validate(task)

    assert read.id == 7
    assert read.title == "Learn FastAPI"
    assert read.description == description
    assert read.is_completed is True
    assert read.created_at == created_at


@pytest.mark.parametrize(
    "missing_field",
    ["id", "title", "description", "is_completed", "created_at"],
)
def test_task_read_requires_all_fields(missing_field: str) -> None:
    payload = dict(TASK_READ_PAYLOAD)
    payload.pop(missing_field)

    with pytest.raises(ValidationError) as exc_info:
        TaskRead.model_validate(payload)

    assert_field_error(exc_info, missing_field)


def test_task_read_serializes_created_at_as_iso_8601_string() -> None:
    created_at = TASK_READ_PAYLOAD["created_at"]
    read = TaskRead.model_validate(TASK_READ_PAYLOAD)

    dumped = read.model_dump(mode="json")

    assert isinstance(dumped["created_at"], str)
    assert datetime.fromisoformat(dumped["created_at"]) == created_at
