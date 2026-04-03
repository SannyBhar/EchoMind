import pytest

from echomind.cues.contracts import CueDeliveryMode, InferenceResultSummary, InferenceStatus
from echomind.cues.planner import (
    build_demo_planner_context,
    build_demo_planning_request,
    plan_deterministic_mvp_variants,
)
from echomind.scoring.composite import composite_score
from echomind.scoring.explain import build_score_explanation
from echomind.scoring.metrics import modality_factor, personalization_factor, response_strength
from echomind.scoring.models import ScoringWeights
from echomind.scoring.pipeline import score_cue_variants
from echomind.tribe.client import TribeRawOutput


def test_response_strength_prefers_raw_outputs() -> None:
    raw_outputs = [
        TribeRawOutput(stimulus_id="s1", cue_id="cue-1", response_score=0.2, token_count=10),
        TribeRawOutput(stimulus_id="s2", cue_id="cue-1", response_score=0.6, token_count=12),
    ]
    aggregate_scores = {"cue-1": 0.9}

    value = response_strength("cue-1", raw_outputs=raw_outputs, aggregate_scores=aggregate_scores)

    assert value == 0.4


def test_modality_factor_values_are_explicit() -> None:
    assert modality_factor(CueDeliveryMode.TEXT_ONLY) == 1.00
    assert modality_factor(CueDeliveryMode.NARRATION) == 1.05
    assert modality_factor(CueDeliveryMode.SLIDESHOW_NARRATION) == 1.10


def test_personalization_factor_uses_level_and_metadata() -> None:
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    text_generic = next(item for item in variants if item.cue_id.endswith("text-generic"))
    text_autobio = next(item for item in variants if item.cue_id.endswith("text-autobiographical"))

    assert personalization_factor(text_generic) == pytest.approx(1.02)
    assert personalization_factor(text_autobio) == pytest.approx(1.14)


def test_composite_score_and_explanation_are_decomposable() -> None:
    weights = ScoringWeights(response_strength=0.8, modality_factor=0.1, personalization_factor=0.1)
    score, response_component, modality_component, personalization_component = composite_score(
        response_strength_value=0.5,
        modality_factor_value=1.10,
        personalization_factor_value=1.12,
        weights=weights,
    )

    assert round(score, 4) == 0.422
    explanation = build_score_explanation(
        response_strength_value=0.5,
        modality_factor_value=1.10,
        personalization_factor_value=1.12,
        response_contribution=response_component,
        modality_contribution=modality_component,
        personalization_contribution=personalization_component,
    )
    assert "Top contribution: response_strength" in explanation


def test_scoring_pipeline_outputs_ranked_scores() -> None:
    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request, context)

    summary = InferenceResultSummary(
        request_id="req-score-001",
        engine_name="tribe-v2",
        status=InferenceStatus.SUCCEEDED,
        aggregate_scores={
            variants[0].cue_id: 0.21,
            variants[1].cue_id: 0.77,
            variants[2].cue_id: 0.33,
            variants[3].cue_id: 0.49,
            variants[4].cue_id: 0.67,
            variants[5].cue_id: 0.59,
        },
    )

    raw_outputs = [
        TribeRawOutput(
            stimulus_id=f"stim-{variant.cue_id}",
            cue_id=variant.cue_id,
            response_score=summary.aggregate_scores[variant.cue_id],
            token_count=20,
        )
        for variant in variants
    ]

    report = score_cue_variants(
        report_id="score-report-demo",
        variants=variants,
        inference_summary=summary,
        raw_outputs=raw_outputs,
    )

    assert report.scores
    ranked = sorted(report.scores, key=lambda item: item.composite_score, reverse=True)
    assert report.scores == ranked
    assert all(item.explanation for item in report.scores)
