"""FastAPI application entrypoint for Vireel."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import SessionLocal
from app.exceptions import register_exception_handlers
from app.models import Project, ProjectStatus
from app.rate_limit import limiter
from app.routers import auth, projects

logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

# Pipeline jobs run as an in-process background task (see
# services/pipeline/runner.py), not a durable job queue -- so any project
# left in one of these non-terminal states was mid-flight when the process
# last stopped and is now orphaned; its background thread is gone and
# nothing will ever move it forward again.
_NON_TERMINAL_STATUSES = (
    ProjectStatus.pending,
    ProjectStatus.downloading,
    ProjectStatus.transcribing,
    ProjectStatus.analyzing,
    ProjectStatus.scripting,
    ProjectStatus.rendering,
)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)


@app.on_event("startup")
def _fail_orphaned_projects() -> None:
    """Mark projects orphaned by a previous process restart as failed.

    Without this, a project interrupted mid-pipeline is stuck forever in a
    non-terminal status with no way to retry (the retry endpoint/button only
    activates for `failed` projects).
    """
    db = SessionLocal()
    try:
        orphaned = db.query(Project).filter(Project.status.in_(_NON_TERMINAL_STATUSES)).all()
        for project in orphaned:
            project.status = ProjectStatus.failed
            project.error_message = "Interrupted by a server restart. Click Retry to run it again."
        if orphaned:
            db.commit()
            logger.warning("Marked %d orphaned in-progress project(s) as failed on startup", len(orphaned))
    finally:
        db.close()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    """Basic liveness check."""
    return {"status": "ok"}
