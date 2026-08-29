"""Pipeline orchestrator: runs the full download -> ... -> render flow for a project.

Runs as a FastAPI `BackgroundTasks` job (i.e. in a background thread of the
same process), so it MUST open its own DB session rather than reusing the
request-scoped one, which is closed as soon as the HTTP response is sent.
"""

import logging
from pathlib import Path

import openai
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import (
    Output,
    OutputCategory,
    OutputStatus,
    OutputType,
    Project,
    ProjectStatus,
    Transcript,
)
from app.services.pipeline.analyze import analyze_highlights
from app.services.pipeline.download import download_source
from app.services.pipeline.extract_audio import extract_audio
from app.services.pipeline.render import render_output
from app.services.pipeline.script import generate_script
from app.services.pipeline.transcribe import transcribe_audio

logger = logging.getLogger(__name__)

# Fixed MVP style mapping — no user picker yet.
_STYLE_MAPPING: dict[OutputType, OutputCategory] = {
    OutputType.trailer_30s: OutputCategory.energetic,
    OutputType.trailer_1min: OutputCategory.dramatic,
    OutputType.summary_3min: OutputCategory.educational,
}


def _ensure_outputs(db: Session, project: Project) -> list[Output]:
    """Create the 3 fixed Output rows for `project` if they don't exist yet.

    Idempotent so a retry doesn't duplicate Output rows.
    """
    outputs = db.query(Output).filter(Output.project_id == project.id).all()
    if outputs:
        return outputs

    outputs = []
    for output_type, category in _STYLE_MAPPING.items():
        output = Output(
            project_id=project.id,
            output_type=output_type,
            category=category,
            status=OutputStatus.pending,
        )
        db.add(output)
        outputs.append(output)
    db.commit()
    for output in outputs:
        db.refresh(output)
    return outputs


def run_pipeline(project_id: int) -> None:
    """Run the full video pipeline for `project_id`, updating status as it progresses."""
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            logger.error("run_pipeline called for a project that no longer exists: id=%s", project_id)
            return

        media_root = Path(settings.MEDIA_ROOT)
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        try:
            project.status = ProjectStatus.downloading
            db.commit()
            video_path = download_source(
                project.source_url,
                project.id,
                media_root,
                cookies_file=settings.YT_COOKIES_FILE or None,
            )
            audio_path = extract_audio(video_path)

            project.status = ProjectStatus.transcribing
            db.commit()
            full_text, segments = transcribe_audio(audio_path, client)

            transcript = db.query(Transcript).filter(Transcript.project_id == project.id).first()
            if transcript is None:
                transcript = Transcript(project_id=project.id, full_text=full_text, segments=segments)
                db.add(transcript)
            else:
                transcript.full_text = full_text
                transcript.segments = segments
                db.add(transcript)
            db.commit()

            project.status = ProjectStatus.analyzing
            db.commit()
            highlights = analyze_highlights(full_text, segments, client)
        except Exception as exc:
            project.status = ProjectStatus.failed
            project.error_message = str(exc)[:2000]
            db.commit()
            logger.exception("Pipeline failed for project %s during download/transcribe/analyze", project_id)
            return

        project.status = ProjectStatus.scripting
        db.commit()

        outputs = _ensure_outputs(db, project)

        project.status = ProjectStatus.rendering
        db.commit()

        any_output_succeeded = False
        for output in outputs:
            if output.status == OutputStatus.completed:
                # Already rendered in a prior run (retry case) — leave it as-is.
                any_output_succeeded = True
                continue
            try:
                output.status = OutputStatus.rendering
                db.commit()

                script = generate_script(output.output_type, output.category, highlights, segments, client)
                output_path = media_root / str(project.id) / f"{output.output_type.value}.mp4"
                duration = render_output(video_path, script["cuts"], script["broll_overlays"], output_path)

                output.file_path = str(output_path)
                output.duration_seconds = duration
                output.status = OutputStatus.completed
                db.commit()
                any_output_succeeded = True
            except Exception:
                logger.exception("Rendering failed for output id=%s (project %s)", output.id, project_id)
                output.status = OutputStatus.failed
                db.commit()

        project.status = ProjectStatus.completed if any_output_succeeded else ProjectStatus.failed
        if not any_output_succeeded:
            project.error_message = "All outputs failed to render"
        db.commit()
    finally:
        db.close()
