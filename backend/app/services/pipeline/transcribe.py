"""Stage: transcribe extracted audio via the OpenAI Whisper API.

The OpenAI client is accepted as a parameter (never constructed here) so
tests can inject a fake/mock client instead of hitting the network.
"""

from pathlib import Path
from typing import Any


def _segment_field(segment: Any, field: str) -> Any:
    """Read a field off a Whisper segment, which may be a dict or a pydantic model."""
    if isinstance(segment, dict):
        return segment[field]
    return getattr(segment, field)


def transcribe_audio(audio_path: Path, client: Any) -> tuple[str, list[dict[str, Any]]]:
    """Transcribe `audio_path` with Whisper, returning (full_text, segments).

    Each item in `segments` is `{"start": float, "end": float, "text": str}`.
    """
    with audio_path.open("rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
        )

    full_text: str = response.text if hasattr(response, "text") else response["text"]
    raw_segments = response.segments if hasattr(response, "segments") else response["segments"]

    segments: list[dict[str, Any]] = [
        {
            "start": float(_segment_field(seg, "start")),
            "end": float(_segment_field(seg, "end")),
            "text": _segment_field(seg, "text"),
        }
        for seg in (raw_segments or [])
    ]

    return full_text, segments
