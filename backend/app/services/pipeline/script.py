"""Stage: turn ranked highlights into a concrete edit script (cuts + B-roll).

Cut selection is deterministic, not another independent LLM call. All three
output types draw from the SAME highlight pool (already spread across the
full source video by `analyze_highlights`), sorted chronologically, and each
output accumulates highlights - in that same chronological order - until it
has enough runtime to fill its own target duration. That guarantees the
30-second output's clips are a strict prefix of the 1-minute output's clips,
which are in turn a prefix of the 3-minute output's clips: every output
samples from across the whole video, and a longer duration just means more
of the same underlying moments get added, rather than three independently
(and inconsistently) chosen edits.
"""

from typing import Any

from app.models import OutputCategory, OutputType

# Target runtime, in seconds, for each output type's main edit.
TARGET_DURATIONS: dict[OutputType, int] = {
    OutputType.trailer_30s: 30,
    OutputType.trailer_1min: 60,
    OutputType.summary_3min: 180,
}

_MAX_BROLL_OVERLAYS = 3
_BROLL_WINDOW_SECONDS = 3.0


def _as_pool(highlights: list[dict[str, Any]], segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Highlights are the pool to draw from; fall back to raw transcript segments
    (score 0) if highlight analysis returned nothing, so an edit can still be built."""
    if highlights:
        return highlights
    return [{"start": s["start"], "end": s["end"], "score": 0.0} for s in segments]


def _select_cuts(
    pool: list[dict[str, Any]], target_duration: float
) -> tuple[list[dict[str, float]], list[dict[str, Any]]]:
    """Walk the pool in chronological order, accumulating clips until
    `target_duration` is covered. Returns (cuts, leftover_pool_items) where
    leftover items (best score first) are candidates for B-roll."""
    ordered = sorted(pool, key=lambda h: float(h["start"]))
    cuts: list[dict[str, float]] = []
    used_ids: set[int] = set()
    total = 0.0

    for item in ordered:
        if total >= target_duration:
            break
        start, end = float(item["start"]), float(item["end"])
        if end <= start:
            continue
        remaining = target_duration - total
        clip_end = end if (end - start) <= remaining else start + remaining
        cuts.append({"start": start, "end": clip_end})
        used_ids.add(id(item))
        total += clip_end - start

    leftover = [
        item for item in sorted(pool, key=lambda h: -float(h.get("score", 0))) if id(item) not in used_ids
    ]
    return cuts, leftover


def _build_broll(cuts: list[dict[str, float]], leftover: list[dict[str, Any]]) -> list[dict[str, float]]:
    """Place up to a few leftover highlights as PiP overlays spread across the
    main edit's own (post-concat) timeline, sourced from other timestamps of
    the same source video."""
    if not cuts or not leftover:
        return []

    main_duration = sum(cut["end"] - cut["start"] for cut in cuts)
    if main_duration <= 0:
        return []

    overlays: list[dict[str, float]] = []
    candidates = leftover[:_MAX_BROLL_OVERLAYS]
    for i, item in enumerate(candidates):
        base_start = (main_duration / (len(candidates) + 1)) * (i + 1)
        base_end = min(base_start + _BROLL_WINDOW_SECONDS, main_duration)
        if base_end <= base_start:
            continue
        source_start = float(item["start"])
        source_end = min(float(item["end"]), source_start + _BROLL_WINDOW_SECONDS)
        if source_end <= source_start:
            continue
        overlays.append(
            {
                "base_start": round(base_start, 3),
                "base_end": round(base_end, 3),
                "source_start": round(source_start, 3),
                "source_end": round(source_end, 3),
            }
        )
    return overlays


def generate_script(
    output_type: OutputType,
    category: OutputCategory,  # noqa: ARG001 - kept for interface stability; not used deterministically yet
    highlights: list[dict[str, Any]],
    segments: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build `{"cuts": [...], "broll_overlays": [...]}` for one output.

    Deterministic (see module docstring): every output type draws from the
    same chronologically-ordered pool and accumulates more of it as
    `output_type`'s target duration grows. B-roll (summary_3min only) is
    drawn from the highest-scoring highlights left over after cuts are chosen.

    Raises `ValueError` if there is no usable timing data (no highlights and
    no transcript segments) to build an edit from.
    """
    target_duration = TARGET_DURATIONS[output_type]
    wants_broll = output_type == OutputType.summary_3min

    source_duration = max((float(s["end"]) for s in segments), default=0.0)
    if source_duration and source_duration <= target_duration:
        # The source is already at or under this output's target length --
        # there's nothing to trim. Use the whole video rather than picking
        # highlights out of it, which would otherwise skip parts of an
        # already-short video instead of covering all of it.
        return {"cuts": [{"start": 0.0, "end": source_duration}], "broll_overlays": []}

    pool = _as_pool(highlights, segments)
    if not pool:
        raise ValueError("No highlights or transcript segments available to build an edit from")

    cuts, leftover = _select_cuts(pool, target_duration)
    if not cuts:
        raise ValueError("Could not select any cuts from the available highlights/segments")

    broll_overlays = _build_broll(cuts, leftover) if wants_broll else []

    return {"cuts": cuts, "broll_overlays": broll_overlays}
