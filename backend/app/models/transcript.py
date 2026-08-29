"""Transcript model — one-to-one with Project."""

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin

if TYPE_CHECKING:
    from app.models.project import Project


class Transcript(Base, CreatedAtMixin):
    """Full transcript + timestamped segments for a project's source video."""

    __tablename__ = "transcripts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    # List of {"start": float, "end": float, "text": str} segments.
    segments: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)

    project: Mapped["Project"] = relationship("Project", back_populates="transcript")
