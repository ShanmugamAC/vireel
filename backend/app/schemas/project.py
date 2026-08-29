"""Pydantic schemas for the project / video-pipeline module."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.exceptions import ValidationError
from app.models import OutputCategory, OutputStatus, OutputType, ProjectStatus
from app.services.pipeline.validate import validate_source_url as _validate_source_url


class ProjectCreate(BaseModel):
    """Payload for POST /projects."""

    source_url: str
    title: str | None = None

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, value: str) -> str:
        """Require an http(s) URL on a supported video-platform host.

        Delegates to `app.services.pipeline.validate.validate_source_url` so
        there is exactly one place defining what's allowed (including the
        SSRF-preventing host allowlist) — this just adapts that check's
        `ValidationError` into pydantic's expected `ValueError` for a clean
        422 response.
        """
        try:
            return _validate_source_url(value)
        except ValidationError as exc:
            raise ValueError(exc.message) from exc


class OutputResponse(BaseModel):
    """A single rendered output belonging to a project."""

    id: int
    output_type: OutputType
    category: OutputCategory
    file_path: str | None
    duration_seconds: float | None
    status: OutputStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectResponse(BaseModel):
    """Full project detail, including its outputs."""

    id: int
    title: str | None
    source_url: str
    status: ProjectStatus
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    outputs: list[OutputResponse]

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """Lightweight project summary for list views."""

    id: int
    title: str | None
    status: ProjectStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
