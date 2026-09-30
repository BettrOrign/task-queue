from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import JobStatus


class TaskBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    payload: dict[str, Any] = Field(default_factory=dict)
    max_retries: int = Field(default=3, ge=0, le=10)


class TaskCreate(TaskBase):
    id: str = Field(..., min_length=1, max_length=36)

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Task ID must not be empty")
        return v


class TaskUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    payload: dict[str, Any] | None = None
    status: JobStatus | None = None
    max_retries: int | None = Field(default=None, ge=0, le=10)


class TaskOut(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: JobStatus
    retries: int
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    error: str | None = None