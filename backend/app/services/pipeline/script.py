"""Stage: turn ranked highlights into a concrete edit script (cuts + B-roll)."""

import json
from typing import Any

from app.config import settings
from app.models import OutputCategory, OutputType

# Target runtime, in seconds, for each output type's main edit.
TARGET_DURATIONS: dict[OutputType, int] = {
    OutputType.trailer_30s: 30,
    OutputType.trailer_1min: 60,
    OutputType.summary_3min: 180,
}

_SYSTEM_PROMPT = (
    "You are a video editor. Given ranked highlight moments and the full timestamped "
    "transcript segments of a source video, produce a concrete edit script. Respond with "
    "STRICT JSON only, no prose, no markdown fences, in exactly this shape: "
    '{"cuts": [{"start": <float seconds>, "end": <float seconds>}], '
    '"broll_overlays": [{"base_start": <float>, "base_end": <float>, '
    '"source_start": <float>, "source_end": <float>}]} '
    "`cuts` is an ordered list of segments from the ORIGINAL source video to concatenate "
    "for the main edit; their combined duration should sum to approximately the requested "
    "target duration (some tolerance is fine). `broll_overlays` describes secondary clips "
    "from OTHER timestamps of the same source video to overlay picture-in-picture during a "
    "window of the main edit — only include these if explicitly asked for below; otherwise "
    "return an empty list for broll_overlays."
)


def generate_script(
    output_type: OutputType,
    category: OutputCategory,
    highlights: list[dict[str, Any]],
    segments: list[dict[str, Any]],
    client: Any,
) -> dict[str, Any]:
    """Generate `{"cuts": [...], "broll_overlays": [...]}` for one output.

    NOTE: for this MVP, B-roll is always sourced from OTHER timestamps of the
    SAME source video (never external stock footage) — `source_start`/
    `source_end` in each `broll_overlays` entry index back into the same
    source video as `cuts`. Swapping in an external stock-footage API later
    would only require changing what `render.py` reads clips from for
    `broll_overlays`; the script's shape is designed to keep working either way.

    Raises `RuntimeError` (with the raw model response included) if the
    model's output cannot be parsed as the expected JSON shape.
    """
    target_duration = TARGET_DURATIONS[output_type]
    wants_broll = output_type == OutputType.summary_3min

    user_prompt = (
        f"Output type: {output_type.value}\n"
        f"Target duration: {target_duration} seconds\n"
        f"Tone/category: {category.value}\n"
        f"Include B-roll overlays: {wants_broll}\n\n"
        f"Ranked highlights (JSON):\n{json.dumps(highlights)}\n\n"
        f"Full timestamped segments (JSON):\n{json.dumps(segments)}\n\n"
        "Produce the edit script now."
    )

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )

    raw_content = response.choices[0].message.content

    try:
        parsed = json.loads(raw_content)
        cuts = parsed["cuts"]
        broll_overlays = parsed.get("broll_overlays", [])
        if not isinstance(cuts, list) or not isinstance(broll_overlays, list):
            raise TypeError("'cuts' and 'broll_overlays' must be lists")
        for cut in cuts:
            float(cut["start"])
            float(cut["end"])
        for overlay in broll_overlays:
            float(overlay["base_start"])
            float(overlay["base_end"])
            float(overlay["source_start"])
            float(overlay["source_end"])
    except (
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        raise RuntimeError(
            f"Failed to parse edit script response as expected JSON: {exc}. Raw response: {raw_content!r}"
        ) from exc

    # Defensive: only summary_3min ever carries B-roll, regardless of what the model returned.
    if not wants_broll:
        broll_overlays = []

    return {"cuts": cuts, "broll_overlays": broll_overlays}
