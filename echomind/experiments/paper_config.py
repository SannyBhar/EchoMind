"""Frozen experiment configuration for the CS439 paper-ready EchoMind slice.

This module captures the exact configuration used to produce the artifacts
referenced in the paper. Treat the values here as a versioned snapshot — bump
PAPER_CONFIG_VERSION when any field changes so reproducibility claims in the
paper remain valid.

Non-clinical research configuration. All findings are simulation-only.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from echomind.scoring.models import ScoringWeights


PAPER_CONFIG_VERSION = "paper.v1.0"


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    version: str
    memory_count: int
    source: str
    categories_min: int
    notes: str


@dataclass(frozen=True)
class CueFamilySpec:
    families: tuple[str, ...]
    template_version: str
    notes: str


@dataclass(frozen=True)
class ComparisonDimension:
    key: str
    groups: tuple[str, ...]
    description: str
    confidence: str  # "strong" | "exploratory" | "limited"
    caveat: str


@dataclass(frozen=True)
class PaperExperimentConfig:
    version: str
    dataset: DatasetSpec
    cue_families: CueFamilySpec
    scoring_weights: ScoringWeights
    dimensions: tuple[ComparisonDimension, ...]
    inference_engine: str
    inference_path: str
    seed_strategy: str
    limitations: tuple[str, ...]
    reproduce_command: str
    artifact_paths: dict[str, str] = field(default_factory=dict)


PAPER_DATASET = DatasetSpec(
    name="echomind-demo-12",
    version="m9.1",
    memory_count=12,
    source="echomind.demo_data.memories.DEMO_MEMORIES",
    categories_min=6,
    notes=(
        "Synthetic, hand-authored memories spanning 10 life-event categories. "
        "No real participant data. Each memory has a deterministic seed; some "
        "carry multiple image URIs to exercise multi-slide rendering."
    ),
)


PAPER_CUE_FAMILIES = CueFamilySpec(
    families=(
        "text_generic",
        "text_autobiographical",
        "narration_neutral",
        "narration_warm",
        "slideshow_neutral",
        "slideshow_warm",
    ),
    template_version="deterministic.m2",
    notes=(
        "Six structurally distinct families derived from a deterministic, "
        "template-driven planner. Generic strips people/place metadata; "
        "autobiographical anchors second-person reconstruction. Warm uses "
        "invitational framing; neutral uses recorded-description framing. "
        "Slideshow narration is a separate text from plain narration."
    ),
)


PAPER_SCORING_WEIGHTS = ScoringWeights(
    response_strength=0.7,
    modality_factor=0.15,
    personalization_factor=0.15,
)


PAPER_DIMENSIONS: tuple[ComparisonDimension, ...] = (
    ComparisonDimension(
        key="warm_vs_neutral",
        groups=("warm", "neutral"),
        description=(
            "Compares warm/invitational vs neutral/factual narration framing "
            "across the same cue scaffolding."
        ),
        confidence="strong",
        caveat=(
            "Cleanest signal in the current pipeline because both groups "
            "follow identical scoring paths and the stub-TRIBE input text "
            "differs only in the framing dimension being studied."
        ),
    ),
    ComparisonDimension(
        key="personalized_vs_generic",
        groups=("personalized", "generic"),
        description=(
            "Compares cues with explicit people/place anchors against a "
            "generic event-type baseline."
        ),
        confidence="exploratory",
        caveat=(
            "Generic cues currently score HIGHER on average. This is an "
            "artifact of the deterministic stub TRIBE client (SHA256 of input "
            "text mapped to [0,1]) interacting with shorter, less constrained "
            "generic prompts. Reported as a contrast in inputs, not as "
            "evidence that generic cues are preferable."
        ),
    ),
    ComparisonDimension(
        key="delivery_mode",
        groups=("text_only", "narration", "slideshow_narration"),
        description=(
            "Compares the three delivery modes the planner produces."
        ),
        confidence="limited",
        caveat=(
            "Only TEXT_ONLY cues actually traverse stub TRIBE today; "
            "NARRATION and SLIDESHOW_NARRATION receive constant heuristic-only "
            "scores via the text-first smoke path. This dimension is included "
            "for completeness but should NOT be read as a modality preference "
            "result."
        ),
    ),
)


PAPER_LIMITATIONS: tuple[str, ...] = (
    "TRIBE is invoked through a deterministic stub client; no real model "
    "inference is performed.",
    "Only the TEXT_ONLY modality reaches the stub; narration and slideshow "
    "scores are heuristic-only constants.",
    "The dataset is synthetic (12 hand-authored memories); there is no human "
    "outcome validation loop.",
    "Composite scores combine a stub-derived response strength with two "
    "explicit heuristic factors (modality, personalization). Submetrics are "
    "always reported alongside the composite to keep the heuristic component "
    "transparent.",
    "Generic-vs-personalized magnitudes reflect stub-text variance and should "
    "not be interpreted as a memory-recall claim.",
)


PAPER_CONFIG = PaperExperimentConfig(
    version=PAPER_CONFIG_VERSION,
    dataset=PAPER_DATASET,
    cue_families=PAPER_CUE_FAMILIES,
    scoring_weights=PAPER_SCORING_WEIGHTS,
    dimensions=PAPER_DIMENSIONS,
    inference_engine="tribe-v2-stub",
    inference_path="text-first smoke path (TEXT_ONLY only)",
    seed_strategy="per-memory deterministic seed embedded in DemoMemorySpec",
    limitations=PAPER_LIMITATIONS,
    reproduce_command=(
        "python3.11 scripts/run_multi_memory_experiments.py "
        "--artifact-root artifacts/experiments/multi_memory && "
        "python3.11 scripts/export_report_artifacts.py "
        "--input artifacts/experiments/multi_memory "
        "--output artifacts/report"
    ),
    artifact_paths={
        "multi_memory_report_json": (
            "artifacts/experiments/multi_memory/aggregate/multi_memory_report.json"
        ),
        "dimension_summary_csv": (
            "artifacts/experiments/multi_memory/aggregate/dimension_summary.csv"
        ),
        "report_root": "artifacts/report",
    },
)
