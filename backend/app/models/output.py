"""Output model — a single rendered trailer/summary belonging to a Project."""

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin

if TYPE_CHECKING:
    from app.models.project import Project


class OutputType(enum.StrEnum):
    """Which of the three deliverables this output is."""

    trailer_30s = "trailer_30s"
    trailer_1min = "trailer_1min"
    summary_3min = "summary_3min"


class OutputCategory(enum.StrEnum):
    """Tone/style applied when scripting and rendering this output."""

    cinematic = "Cinematic"
    energetic = "Energetic"
    educational = "Educational"
    dramatic = "Dramatic"


class OutputStatus(enum.StrEnum):
    """Render status of a single output."""

    pending = "pending"
    rendering = "rendering"
    completed = "completed"
    failed = "failed"


class Output(Base, CreatedAtMixin):
    """A single rendered video belonging to a Project (expect 3 per completed project)."""

    __tablename__ = "outputs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    output_type: Mapped[OutputType] = mapped_column(
        SqlEnum(OutputType, name="output_type", native_enum=True), nullable=False
    )
    category: Mapped[OutputCategory] = mapped_column(
        SqlEnum(OutputCategory, name="output_category", native_enum=True), nullable=False
    )
    file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[OutputStatus] = mapped_column(
        SqlEnum(OutputStatus, name="output_status", native_enum=True),
        default=OutputStatus.pending,
        server_default=OutputStatus.pending.value,
        nullable=False,
        index=True,
    )

    project: Mapped["Project"] = relationship("Project", back_populates="outputs")
