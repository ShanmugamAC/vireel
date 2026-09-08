"""Stage: ask GPT to identify highlight-worthy moments in the transcript."""

import json
from typing import Any

from app.config import settings

_SYSTEM_PROMPT = (
    "You are a video editor's assistant. Given a timestamped transcript, identify the "
    "moments that would make the strongest hooks or highlights across the WHOLE video, not "
    "just its opening. Aim for 8-15 highlights (fewer only if the video is genuinely too short "
    "to support that many) spread across the beginning, middle, and end, so downstream edits of "
    "different lengths have enough distinct material to draw from instead of all reusing the "
    "same one or two clips. Respond with STRICT JSON only, no prose, no markdown fences, in "
    "exactly this shape: "
    '{"highlights": [{"start": <float seconds>, "end": <float seconds>, '
    '"score": <float 0-1>, "reason": "<short string>"}]} '
    "Order the list from best to worst highlight."
)


def analyze_highlights(transcript_text: str, segments: list[dict[str, Any]], client: Any) -> list[dict[str, Any]]:
    """Return a list of `{"start", "end", "score", "reason"}` highlight moments, best first.

    Raises `RuntimeError` (with the raw model response included) if the model's
    output cannot be parsed as the expected JSON shape.
    """
    user_prompt = (
        f"Full transcript:\n{transcript_text}\n\n"
        f"Timestamped segments (JSON):\n{json.dumps(segments)}\n\n"
        "Identify the best highlight moments now."
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
        highlights = parsed["highlights"] if isinstance(parsed, dict) else parsed
        if not isinstance(highlights, list):
            raise TypeError("'highlights' is not a list")
        for item in highlights:
            float(item["start"])
            float(item["end"])
            float(item["score"])
            str(item["reason"])
    except (
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        raise RuntimeError(
            f"Failed to parse highlight analysis response as expected JSON: {exc}. Raw response: {raw_content!r}"
        ) from exc

    return highlights
