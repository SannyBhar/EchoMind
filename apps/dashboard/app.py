"""Streamlit experiment inspection dashboard for EchoMind."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from echomind.dashboard.service import (
    DashboardInspectionResult,
    collect_stimulus_artifact_previews,
    run_demo_inspection,
)
from echomind.dashboard.view_models import (
    cue_variant_rows,
    group_rows,
    rendered_stimulus_rows,
    score_rows,
)

SESSION_KEY = "dashboard_inspection_result"


def dashboard_title() -> str:
    """Return dashboard title for smoke tests and page rendering."""

    return "EchoMind Dashboard"


def render_page() -> None:
    """Render a minimal but functional inspection dashboard."""

    st.set_page_config(page_title=dashboard_title(), layout="wide")
    st.title(dashboard_title())
    st.caption(
        "Inspection interface for non-clinical, simulation-based cue comparison and ranking."
    )
    st.warning(
        "EchoMind is non-clinical research software. Outputs are in-silico simulation artifacts "
        "and not diagnostic or treatment guidance."
    )
    st.info("Current smoke inference path is text-first (TRIBE preprocess filters to text-only).")

    artifact_root = st.text_input("Artifact root", value="artifacts/dashboard")
    result = _load_inspection_result(artifact_root=artifact_root)
    if result is None:
        st.error("Demo inspection run is unavailable. Verify local environment and retry.")
        return

    _render_overview(result)
    _render_memory(result)
    _render_cues(result)
    _render_rendered_outputs(result)
    _render_inference(result)
    _render_scoring(result)
    _render_experiments(result)


def _load_inspection_result(artifact_root: str) -> DashboardInspectionResult | None:
    refresh = st.button("Run / Refresh Demo Inspection", use_container_width=True)
    if refresh or SESSION_KEY not in st.session_state:
        with st.spinner("Running deterministic demo pipeline..."):
            try:
                st.session_state[SESSION_KEY] = run_demo_inspection(artifact_root=artifact_root)
            except Exception:
                return None
    return st.session_state.get(SESSION_KEY)


def _render_overview(result: DashboardInspectionResult) -> None:
    st.header("Project Overview")
    st.write(result.milestone_summary)
    st.write(
        {
            "planning_request_id": result.planning_request.request_id,
            "engine_name": result.inference_result.summary.engine_name,
            "inference_status": result.inference_result.summary.status.value,
            "rendered_stimulus_count": len(result.rendered_stimulus_manifest.stimuli),
            "score_count": len(result.scoring_report.scores),
            "experiment_report_path": result.experiment_report_path,
        }
    )


def _render_memory(result: DashboardInspectionResult) -> None:
    memory = result.memory_overview
    st.header("Demo Memory Overview")
    st.write(
        {
            "source": memory.source,
            "external_id": memory.external_id,
            "title": memory.title,
            "narrative": memory.narrative,
            "memory_type": memory.memory_type,
            "place": memory.place,
            "people": memory.people,
            "asset_count": len(memory.assets),
            "notes": memory.notes,
        }
    )
    if memory.assets:
        st.subheader("Assets")
        st.dataframe(memory.assets, use_container_width=True)


def _render_cues(result: DashboardInspectionResult) -> None:
    st.header("Generated Cue Variants")
    st.dataframe(cue_variant_rows(result.planned_variants), use_container_width=True)
    for variant in result.planned_variants:
        with st.expander(f"Cue: {variant.cue_id}", expanded=False):
            st.json(variant.model_dump(mode="json"))


def _render_rendered_outputs(result: DashboardInspectionResult) -> None:
    st.header("Rendered Stimulus Outputs")
    st.caption(
        "Narration audio and slideshow video artifacts are deterministic stub-backed placeholders."
    )
    manifest = result.rendered_stimulus_manifest
    st.dataframe(rendered_stimulus_rows(manifest), use_container_width=True)

    for stimulus in manifest.stimuli:
        with st.expander(f"Stimulus: {stimulus.stimulus_id}", expanded=False):
            st.json(stimulus.model_dump(mode="json"))
            previews = collect_stimulus_artifact_previews(stimulus=stimulus)
            for preview in previews:
                st.write(
                    {
                        "artifact_key": preview.key,
                        "path": preview.path,
                        "exists": preview.exists,
                    }
                )
                if preview.preview:
                    st.code(preview.preview, language="text")


def _render_inference(result: DashboardInspectionResult) -> None:
    st.header("Smoke Inference Results")
    inference = result.inference_result
    st.subheader("Request Metadata")
    st.json(inference.batch_input.model_dump(mode="json"))
    st.subheader("Summary")
    st.json(inference.summary.model_dump(mode="json"))
    st.subheader("Artifacts")
    st.write(
        {
            "run_dir": str(inference.artifacts.run_dir),
            "request_path": str(inference.artifacts.request_path),
            "raw_outputs_path": str(inference.artifacts.raw_outputs_path),
            "summary_path": str(inference.artifacts.summary_path),
            "metadata_path": str(inference.artifacts.metadata_path),
        }
    )


def _render_scoring(result: DashboardInspectionResult) -> None:
    st.header("Scoring Breakdown")
    st.dataframe(score_rows(result.scoring_report.scores), use_container_width=True)
    for score in result.scoring_report.scores:
        with st.expander(f"Score Detail: {score.cue_id}", expanded=False):
            st.json(
                {
                    "response_strength": score.response_strength,
                    "modality_factor": score.modality_factor,
                    "personalization_factor": score.personalization_factor,
                    "composite_score": score.composite_score,
                    "explanation": score.explanation,
                    "metadata": score.metadata,
                }
            )


def _render_experiments(result: DashboardInspectionResult) -> None:
    st.header("Grouped Experiment Comparisons")
    st.caption(
        "Comparisons are deterministic summaries of simulation outputs for "
        "inspection, not clinical outcomes."
    )
    for dimension in result.experiment_report.grouped_comparisons:
        st.subheader(dimension.dimension)
        rows = group_rows(dimension)
        st.dataframe(rows, use_container_width=True)
        chart_data = {
            group["group_key"]: float(group["avg_composite_score"]) for group in rows
        }
        st.bar_chart(chart_data)

    st.subheader("Ranked Cues")
    st.write([score.cue_id for score in result.experiment_report.ranked_cues])
    st.json(result.experiment_report.model_dump(mode="json"))

    report_path = Path(result.experiment_report_path)
    if report_path.exists():
        st.caption(f"Saved report artifact: {report_path}")


if __name__ == "__main__":
    render_page()
