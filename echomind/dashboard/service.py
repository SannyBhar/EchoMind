"""Thin dashboard service layer for deterministic demo inspection flows."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from echomind.cues.contracts import (
    CueDeliveryMode,
    CueGenerationRequest,
    CueVariantSpec,
    RenderedStimulus,
    StimulusManifest,
)
from echomind.cues.planner import (
    build_demo_planner_context,
    build_demo_planning_request,
    plan_deterministic_mvp_variants,
)
from echomind.db.models import Memory
from echomind.db.session import SessionLocal, session_scope
from echomind.experiments.models import ExperimentComparisonReport
from echomind.experiments.reports import build_experiment_report, save_experiment_report
from echomind.media.renderer import DeterministicMediaRenderer
from echomind.scoring.models import ScoringReport
from echomind.scoring.pipeline import score_cue_variants
from echomind.tribe.infer import TribeInferenceRunResult, run_tribe_inference

MILESTONE_SUMMARY = (
    "Validated deterministic pipeline: planner -> renderer -> text-first TRIBE smoke "
    "-> scoring -> grouped experiment comparison."
)


@dataclass(slots=True)
class SeededMemoryOverview:
    """Memory overview payload for inspection UI."""

    source: str
    external_id: str
    title: str
    narrative: str
    memory_type: str
    people: list[str] = field(default_factory=list)
    place: str | None = None
    assets: list[dict[str, str]] = field(default_factory=list)
    notes: str | None = None


@dataclass(slots=True)
class ArtifactPreview:
    """Preview metadata for a rendered artifact file."""

    key: str
    path: str
    exists: bool
    preview: str | None


@dataclass(slots=True)
class DashboardInspectionResult:
    """Full deterministic demo pipeline output for dashboard inspection."""

    milestone_summary: str
    memory_overview: SeededMemoryOverview
    planning_request: CueGenerationRequest
    planned_variants: list[CueVariantSpec]
    rendered_stimulus_manifest: StimulusManifest
    inference_result: TribeInferenceRunResult
    scoring_report: ScoringReport
    experiment_report: ExperimentComparisonReport
    experiment_report_path: str


def load_seeded_memory_overview(external_id: str = "demo-memory-001") -> SeededMemoryOverview:
    """Load seeded demo memory details from DB with deterministic fallback."""

    memory = _load_seeded_memory_from_db(external_id=external_id)
    if memory is None:
        context = build_demo_planner_context()
        assets = [{"asset_type": "image", "uri": uri} for uri in context.image_asset_uris]
        return SeededMemoryOverview(
            source="fallback",
            external_id=context.memory_id,
            title=context.memory_title,
            narrative=context.memory_summary,
            memory_type="episodic",
            people=sorted(context.people_names),
            place=context.place_name,
            assets=assets,
            notes="Database memory unavailable; showing deterministic fallback context.",
        )

    return SeededMemoryOverview(
        source="database",
        external_id=memory.external_id,
        title=memory.title,
        narrative=memory.narrative,
        memory_type=memory.memory_type.value,
        people=sorted(person.full_name for person in memory.people),
        place=memory.place.name if memory.place else None,
        assets=[
            {
                "asset_type": asset.asset_type.value,
                "uri": asset.uri,
                "description": asset.description or "",
            }
            for asset in memory.assets
        ],
    )


def run_demo_inspection(
    artifact_root: str | Path = "artifacts/dashboard",
) -> DashboardInspectionResult:
    """Execute deterministic demo pipeline and return inspection-ready outputs."""

    request = build_demo_planning_request()
    context = build_demo_planner_context()
    variants = plan_deterministic_mvp_variants(request=request, context=context)

    root = Path(artifact_root)
    renderer = DeterministicMediaRenderer(artifact_root=root / "media")
    manifest = renderer.render_manifest(
        memory_id=request.memory_id,
        variants=variants,
        manifest_id=f"manifest-{request.memory_id}-dashboard",
    )

    inference = run_tribe_inference(
        manifest=manifest,
        request_id=f"{request.request_id}-dashboard",
        artifact_root=root / "inference",
        supported_modalities={CueDeliveryMode.TEXT_ONLY},
    )

    scoring_report = score_cue_variants(
        report_id=f"score-{request.request_id}-dashboard",
        variants=variants,
        inference_summary=inference.summary,
        raw_outputs=inference.raw_outputs,
    )

    experiment_report = build_experiment_report(
        experiment_id=f"experiment-{request.request_id}-dashboard",
        score_report=scoring_report,
    )
    experiment_report_path = save_experiment_report(report=experiment_report, artifact_root=root)

    return DashboardInspectionResult(
        milestone_summary=MILESTONE_SUMMARY,
        memory_overview=load_seeded_memory_overview(external_id=request.memory_id),
        planning_request=request,
        planned_variants=variants,
        rendered_stimulus_manifest=manifest,
        inference_result=inference,
        scoring_report=scoring_report,
        experiment_report=experiment_report,
        experiment_report_path=str(experiment_report_path),
    )


def collect_stimulus_artifact_previews(
    stimulus: RenderedStimulus,
    max_chars: int = 1200,
) -> list[ArtifactPreview]:
    """Collect deterministic previews for known rendered artifact files."""

    previews: list[ArtifactPreview] = []
    metadata = stimulus.metadata or {}
    artifact_keys = sorted(
        key for key in metadata if key.endswith("_artifact") and isinstance(metadata[key], str)
    )
    for key in artifact_keys:
        path_value = str(metadata[key])
        path = Path(path_value)
        exists = path.exists()
        preview = None
        if exists and path.is_file():
            preview = path.read_text(encoding="utf-8", errors="replace")
            if len(preview) > max_chars:
                preview = f"{preview[:max_chars]}\n... (truncated)"
        previews.append(
            ArtifactPreview(
                key=key,
                path=path_value,
                exists=exists,
                preview=preview,
            )
        )

    return previews


def _load_seeded_memory_from_db(external_id: str) -> Memory | None:
    """Return one memory graph by external id, if DB access is available."""

    try:
        with session_scope(SessionLocal) as session:
            stmt = (
                select(Memory)
                .where(Memory.external_id == external_id)
                .options(
                    selectinload(Memory.place),
                    selectinload(Memory.people),
                    selectinload(Memory.assets),
                )
            )
            return session.scalar(stmt)
    except Exception:
        return None
