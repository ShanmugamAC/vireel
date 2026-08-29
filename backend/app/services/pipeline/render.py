"""Stage: render the final edit (cuts + optional B-roll PiP overlays) with ffmpeg.

Builds a single `ffmpeg -filter_complex ...` graph and invokes it via
`subprocess.run` with an explicit argument list — never `shell=True`, never a
string-interpolated shell command — since every timestamp here ultimately
traces back to an LLM-generated script derived from user-supplied content.
"""

import subprocess
from pathlib import Path
from typing import Any

# Picture-in-picture overlay is scaled to ~30% of the main video's dimensions
# and pinned to the bottom-right corner with a small margin.
_PIP_SCALE_FACTOR = 0.3
_PIP_MARGIN_PX = 20


def _fmt(value: float) -> str:
    """Format a timestamp/number for embedding in an ffmpeg filter expression."""
    return f"{float(value):.3f}"


def _build_filter_complex(cuts: list[dict[str, Any]], broll_overlays: list[dict[str, Any]]) -> tuple[str, str, str]:
    """Build the filter_complex graph string.

    Returns (filter_complex, final_video_label, final_audio_label).
    """
    parts: list[str] = []
    concat_refs: list[str] = []

    for i, cut in enumerate(cuts):
        start, end = _fmt(cut["start"]), _fmt(cut["end"])
        parts.append(f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}]")
        parts.append(f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}]")
        concat_refs.append(f"[v{i}][a{i}]")

    parts.append(f"{''.join(concat_refs)}concat=n={len(cuts)}:v=1:a=1[vmain][amain]")

    current_v_label = "vmain"
    for j, overlay in enumerate(broll_overlays):
        base_start = _fmt(overlay["base_start"])
        base_end = _fmt(overlay["base_end"])
        source_start = _fmt(overlay["source_start"])
        source_end = _fmt(overlay["source_end"])
        broll_label = f"broll{j}"

        # Shift the B-roll clip's own timeline to start at base_start (rather than 0)
        # so the overlay filter's `between(t, base_start, base_end)` window lines up
        # with the actual content of the clip instead of its first frames.
        parts.append(
            f"[0:v]trim=start={source_start}:end={source_end},"
            f"setpts=PTS-STARTPTS+{base_start}/TB,"
            f"scale=trunc(iw*{_PIP_SCALE_FACTOR}/2)*2:trunc(ih*{_PIP_SCALE_FACTOR}/2)*2[{broll_label}]"
        )

        next_v_label = f"vov{j}"
        parts.append(
            f"[{current_v_label}][{broll_label}]overlay="
            f"x=main_w-overlay_w-{_PIP_MARGIN_PX}:y=main_h-overlay_h-{_PIP_MARGIN_PX}:"
            f"enable='between(t,{base_start},{base_end})':eof_action=pass[{next_v_label}]"
        )
        current_v_label = next_v_label

    return ";".join(parts), current_v_label, "amain"


def render_output(
    source_video: Path,
    cuts: list[dict[str, Any]],
    broll_overlays: list[dict[str, Any]],
    output_path: Path,
) -> float:
    """Render `cuts` (+ optional `broll_overlays`) from `source_video` to `output_path`.

    Returns the final rendered duration in seconds (probed via ffprobe).
    Raises `ValueError` if `cuts` is empty, or `subprocess.CalledProcessError`
    if ffmpeg/ffprobe fail.
    """
    if not cuts:
        raise ValueError("cuts must contain at least one segment to render")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    filter_complex, video_label, audio_label = _build_filter_complex(cuts, broll_overlays)

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source_video),
        "-filter_complex",
        filter_complex,
        "-map",
        f"[{video_label}]",
        "-map",
        f"[{audio_label}]",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    return _probe_duration(output_path)


def _probe_duration(video_path: Path) -> float:
    """Probe a video file's duration in seconds via ffprobe."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return float(result.stdout.strip())
