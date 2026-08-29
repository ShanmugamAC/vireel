"""Project endpoints: create/list/get/delete/retry projects and download outputs."""

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.exceptions import NotFoundError
from app.models import OutputStatus, User
from app.rate_limit import limiter
from app.schemas.project import ProjectCreate, ProjectListResponse, ProjectResponse
from app.services import project_service
from app.services.pipeline.runner import run_pipeline

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")
async def create_project(
    request: Request,
    payload: ProjectCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Create a new project and kick off its pipeline run in the background."""
    project = project_service.create_project(db, current_user, payload.source_url, payload.title)
    background_tasks.add_task(run_pipeline, project.id)
    return ProjectResponse.model_validate(project)


@router.get("/", response_model=list[ProjectListResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProjectListResponse]:
    """List all projects owned by the current user."""
    projects = project_service.list_projects(db, current_user)
    return [ProjectListResponse.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Get a single project's full detail, including its outputs."""
    project = project_service.get_project(db, current_user, project_id)
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a project and its media directory."""
    project_service.delete_project(db, current_user, project_id)


@router.post("/{project_id}/retry", response_model=ProjectResponse)
async def retry_project(
    project_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Retry a failed project's pipeline run."""
    project = project_service.retry_project(db, current_user, project_id)
    background_tasks.add_task(run_pipeline, project.id)
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}/outputs/{output_id}/download")
async def download_output(
    project_id: int,
    output_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    """Download a single completed Output's rendered file."""
    project = project_service.get_project(db, current_user, project_id)
    output = next((o for o in project.outputs if o.id == output_id), None)

    if output is None or output.status != OutputStatus.completed or not output.file_path:
        raise NotFoundError("Output")

    file_path = Path(output.file_path)
    if not file_path.exists():
        raise NotFoundError("Output")

    return FileResponse(path=file_path, filename=f"{output.output_type.value}.mp4")
