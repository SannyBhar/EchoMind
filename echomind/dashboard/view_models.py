"""View-model helpers for Streamlit dashboard rendering."""

from __future__ import annotations

from echomind.cues.contracts import CueVariantSpec, StimulusManifest
from echomind.experiments.models import DimensionComparison
from echomind.scoring.models import ScoreBreakdown


def cue_variant_rows(variants: list[CueVariantSpec]) -> list[dict[str, str]]:
    """Return compact cue rows for table display."""

    return [
        {
            "cue_id": variant.cue_id,
            "delivery_mode": variant.delivery_mode.value,
            "tone": str(variant.tone),
            "personalization_level": str(variant.personalization_level),
            "variant_family": str(variant.metadata.get("variant_family", "")),
        }
        for variant in variants
    ]


def rendered_stimulus_rows(manifest: StimulusManifest) -> list[dict[str, str]]:
    """Return compact rendered stimulus rows for table display."""

    return [
        {
            "stimulus_id": stimulus.stimulus_id,
            "cue_id": stimulus.cue_id,
            "delivery_mode": stimulus.delivery_mode.value,
            "narration_audio_uri": stimulus.narration_audio_uri or "",
            "slide_image_count": str(len(stimulus.slide_image_uris)),
        }
        for stimulus in manifest.stimuli
    ]


def score_rows(scores: list[ScoreBreakdown]) -> list[dict[str, str | float]]:
    """Return decomposed score rows for table display."""

    return [
        {
            "cue_id": score.cue_id,
            "delivery_mode": score.delivery_mode.value,
            "response_strength": round(score.response_strength, 4),
            "modality_factor": round(score.modality_factor, 4),
            "personalization_factor": round(score.personalization_factor, 4),
            "composite_score": round(score.composite_score, 4),
        }
        for score in scores
    ]


def group_rows(dimension: DimensionComparison) -> list[dict[str, str | float | int]]:
    """Return grouped summary rows for one comparison dimension."""

    return [
        {
            "group_key": group.group_key,
            "count": group.count,
            "avg_composite_score": round(group.avg_composite_score, 4),
            "max_composite_score": round(group.max_composite_score, 4),
            "min_composite_score": round(group.min_composite_score, 4),
        }
        for group in dimension.groups
    ]
