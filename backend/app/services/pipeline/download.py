"""Stage: download the source video via the yt-dlp Python library.

Deliberately uses the `yt_dlp` package API rather than shelling out to a
`yt-dlp` CLI string — this avoids any subprocess/shell-injection surface for
a user-supplied URL entirely.
"""

import logging
from pathlib import Path

import yt_dlp

logger = logging.getLogger(__name__)

# Best available mp4 video+audio, capped at 1080p, merged into a single mp4.
_FORMAT_SPEC = "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4][height<=1080]/best"


def download_source(source_url: str, project_id: int, media_root: Path) -> Path:
    """Download `source_url` into `{media_root}/{project_id}/source.<ext>`.

    Returns the Path to the downloaded video file. Raises whatever `yt_dlp`
    raises (typically `yt_dlp.utils.DownloadError`) on failure.
    """
    project_dir = media_root / str(project_id)
    project_dir.mkdir(parents=True, exist_ok=True)
    out_template = str(project_dir / "source.%(ext)s")

    ydl_opts = {
        "format": _FORMAT_SPEC,
        "outtmpl": out_template,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "logger": logger,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(source_url, download=True)

    # The merged/downloaded file's exact extension depends on the source and
    # available postprocessors, so locate it by its fixed "source.*" stem
    # rather than trusting a single predicted filename.
    matches = sorted(project_dir.glob("source.*"))
    if not matches:
        raise FileNotFoundError(f"yt-dlp reported success but no output file was found in {project_dir}")
    return matches[0]
