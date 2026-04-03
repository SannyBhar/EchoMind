"""Aggregate utilities for TRIBE inference outputs."""

from __future__ import annotations

from echomind.cues.contracts import InferenceResultSummary, InferenceStatus
from echomind.tribe.client import TribeRawOutput


def build_inference_summary(
    request_id: str,
    engine_name: str,
    outputs: list[TribeRawOutput],
    notes: str | None = None,
) -> InferenceResultSummary:
    """Build a lightweight ranking summary from raw simulation outputs."""

    ranked = sorted(outputs, key=lambda item: item.response_score, reverse=True)
    aggregate_scores = {output.cue_id: output.response_score for output in ranked}
    ranked_cue_ids = [output.cue_id for output in ranked]

    status = InferenceStatus.SUCCEEDED if outputs else InferenceStatus.FAILED

    return InferenceResultSummary(
        request_id=request_id,
        engine_name=engine_name,
        status=status,
        ranked_cue_ids=ranked_cue_ids,
        aggregate_scores=aggregate_scores,
        summary_metadata={
            "stimulus_count": len(outputs),
            "top_score": ranked[0].response_score if ranked else 0.0,
        },
        notes=notes,
    )
