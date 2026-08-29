"""SQLAlchemy models package.

Import everything from here (`from app.models import User, Project, ...`) so
that all model classes are registered on `Base.metadata` before Alembic
autogenerate or `Base.metadata.create_all()` run.
"""

from app.models.base import Base, CreatedAtMixin, TimestampMixin
from app.models.output import Output, OutputCategory, OutputStatus, OutputType
from app.models.project import Project, ProjectStatus
from app.models.refresh_token import RefreshToken
from app.models.transcript import Transcript
from app.models.user import User

__all__ = [
    "Base",
    "CreatedAtMixin",
    "Output",
    "OutputCategory",
    "OutputStatus",
    "OutputType",
    "Project",
    "ProjectStatus",
    "RefreshToken",
    "TimestampMixin",
    "Transcript",
    "User",
]
