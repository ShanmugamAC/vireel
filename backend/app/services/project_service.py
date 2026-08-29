"""Business logic for creating, listing, and managing projects."""

import logging
import shutil
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.exceptions import ConflictError, NotFoundError
from app.models import Project, ProjectStatus, User
from app.services.pipeline.validate import validate_source_url

logger = logging.getLogger(__name__)


def create_project(db: Session, user: User, source_url: str, title: str | None) -> Project:
    """Validate `source_url` and create a new pending Project for `user`.

    Output rows are intentionally NOT created here — `runner.run_pipeline`
    creates them (using the fixed style mapping) on its first run.
    """
    validated_url = validate_source_url(source_url)

    project = Project(
        user_id=user.id,
        title=title,
        source_url=validated_url,
        status=ProjectStatus.pending,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def list_projects(db: Session, user: User) -> list[Project]:
    """List all projects owned by `user`, newest first."""
    return (
        db.query(Project)
        .filter(Project.user_id == user.id)
        .order_by(Project.created_at.desc())
        .all()
    )


def get_project(db: Session, user: User, project_id: int) -> Project:
    """Fetch a single project owned by `user`, raising NotFoundError otherwise."""
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == user.id)
        .first()
    )
    if project is None:
        raise NotFoundError("Project")
    return project


def delete_project(db: Session, user: User, project_id: int) -> None:
    """Delete a project (and best-effort its on-disk media directory)."""
    project = get_project(db, user, project_id)
    media_dir = Path(settings.MEDIA_ROOT) / str(project.id)

    db.delete(project)
    db.commit()

    try:
        if media_dir.exists():
            shutil.rmtree(media_dir)
    except OSError:
        logger.warning("Failed to remove media directory %s for project %s", media_dir, project_id, exc_info=True)


def retry_project(db: Session, user: User, project_id: int) -> Project:
    """Reset a failed project back to pending so its pipeline can be re-run."""
    project = get_project(db, user, project_id)
    if project.status != ProjectStatus.failed:
        raise ConflictError("Only failed projects can be retried")

    project.status = ProjectStatus.pending
    project.error_message = None
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
