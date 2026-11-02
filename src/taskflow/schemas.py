"""Pydantic schemas for the TaskFlow task API."""

from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StrictBool,
    field_validator,
)


def _strip_title(value: object) -> object:
    """Trim a title before length validation."""
    if isinstance(value, str):
        return value.strip()
    return value


_TrimmedTitle = Annotated[
    str,
    BeforeValidator(_strip_title),
    Field(min_length=1, max_length=200),
]


class TaskCreate(BaseModel):
    """Request body for creating a task."""

    model_config = ConfigDict(extra="ignore")

    title: _TrimmedTitle
    description: str | None = None


class TaskUpdate(BaseModel):
    """Request body for partially updating a task."""

    model_config = ConfigDict(extra="ignore")

    title: _TrimmedTitle | None = None
    description: str | None = None
    is_completed: StrictBool | None = None

    @field_validator("title", "is_completed")
    @classmethod
    def reject_explicit_null(cls, value: object) -> object:
        """Reject explicit nulls while still allowing omitted fields."""
        if value is None:
            raise ValueError("must not be null")
        return value


class TaskRead(BaseModel):
    """Response body for a task."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    is_completed: bool
    created_at: datetime
