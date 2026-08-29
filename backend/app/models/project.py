"""Project model — one video-to-trailer pipeline run."""

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.output import Output
    from app.models.transcript import Transcript
    from app.models.user import User


class ProjectStatus(enum.StrEnum):
    """Pipeline stage a project is currently in."""

    pending = "pending"
    downloading = "downloading"
    transcribing = "transcribing"
    analyzing = "analyzing"
    scripting = "scripting"
    rendering = "rendering"
    completed = "completed"
    failed = "failed"


class Project(Base, TimestampMixin):
    """A single submitted video and its trailer-generation pipeline run."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(
        SqlEnum(ProjectStatus, name="project_status", native_enum=True),
        default=ProjectStatus.pending,
        server_default=ProjectStatus.pending.value,
        nullable=False,
        index=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="projects")
    transcript: Mapped["Transcript | None"] = relationship(
        "Transcript",
        back_populates="project",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    outputs: Mapped[list["Output"]] = relationship(
        "Output",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
