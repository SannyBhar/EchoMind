"""Scoring pipeline utilities for cue/inference comparison."""

from __future__ import annotations

from echomind.cues.contracts import CueVariantSpec, InferenceResultSummary
from echomind.scoring.composite import composite_score
from echomind.scoring.explain import build_score_explanation
from echomind.scoring.metrics import modality_factor, personalization_factor, response_strength
from echomind.scoring.models import ScoreBreakdown, ScoringReport, ScoringWeights
from echomind.tribe.client import TribeRawOutput


def score_cue_variants(
    report_id: str,
    variants: list[CueVariantSpec],
    inference_summary: InferenceResultSummary,
    raw_outputs: list[TribeRawOutput],
    weights: ScoringWeights | None = None,
) -> ScoringReport:
    """Compute transparent scoring outputs for cue variants."""

    resolved_weights = weights or ScoringWeights()

    scores: list[ScoreBreakdown] = []
    for variant in variants:
        response_value = response_strength(
            cue_id=variant.cue_id,
            raw_outputs=raw_outputs,
            aggregate_scores=inference_summary.aggregate_scores,
        )
        modality_value = modality_factor(variant.delivery_mode)
        personalization_value = personalization_factor(variant)

        composite, response_contribution, modality_contribution, personalization_contribution = (
            composite_score(
                response_strength_value=response_value,
                modality_factor_value=modality_value,
                personalization_factor_value=personalization_value,
                weights=resolved_weights,
            )
        )

        explanation = build_score_explanation(
            response_strength_value=response_value,
            modality_factor_value=modality_value,
            personalization_factor_value=personalization_value,
            response_contribution=response_contribution,
            modality_contribution=modality_contribution,
            personalization_contribution=personalization_contribution,
        )

        scores.append(
            ScoreBreakdown(
                cue_id=variant.cue_id,
                delivery_mode=variant.delivery_mode,
                tone=str(variant.tone),
                personalization_level=str(variant.personalization_level),
                response_strength=response_value,
                modality_factor=modality_value,
                personalization_factor=personalization_value,
                composite_score=composite,
                contribution_response_strength=response_contribution,
                contribution_modality_factor=modality_contribution,
                contribution_personalization_factor=personalization_contribution,
                explanation=explanation,
                metadata=variant.metadata,
            )
        )

    ranked_scores = sorted(scores, key=lambda item: item.composite_score, reverse=True)
    return ScoringReport(report_id=report_id, scores=ranked_scores)
