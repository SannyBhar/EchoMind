"""Deterministic artifact persistence for TRIBE integration outputs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from echomind.cues.contracts import InferenceResultSummary
from echomind.tribe.client import TribeRawOutput

TRIBE_ARTIFACT_VERSION = "mvp.tribe.v1"


@dataclass(slots=True)
class TribeRunArtifacts:
    """Filesystem paths for a persisted TRIBE run."""

    run_dir: Path
    request_path: Path
    raw_outputs_path: Path
    summary_path: Path
    metadata_path: Path


def save_tribe_run_artifacts(
    artifact_root: str | Path,
    request_id: str,
    request_payload: dict,
    raw_outputs: list[TribeRawOutput],
    summary: InferenceResultSummary,
) -> TribeRunArtifacts:
    """Persist request/raw/summary artifacts with deterministic paths."""

    root = Path(artifact_root)
    run_dir = root / "tribe" / _sanitize_id(request_id)
    run_dir.mkdir(parents=True, exist_ok=True)

    request_path = run_dir / "request.json"
    raw_outputs_path = run_dir / "raw_outputs.json"
    summary_path = run_dir / "summary.json"
    metadata_path = run_dir / "metadata.json"

    request_path.write_text(json.dumps(request_payload, indent=2, default=str), encoding="utf-8")
    raw_outputs_path.write_text(
        json.dumps([item.model_dump(mode="json") for item in raw_outputs], indent=2),
        encoding="utf-8",
    )
    summary_path.write_text(
        json.dumps(summary.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )
    metadata_payload = {
        "artifact_version": TRIBE_ARTIFACT_VERSION,
        "request_id": request_id,
        "raw_output_count": len(raw_outputs),
        "summary_status": summary.status.value,
    }
    metadata_path.write_text(json.dumps(metadata_payload, indent=2), encoding="utf-8")

    return TribeRunArtifacts(
        run_dir=run_dir,
        request_path=request_path,
        raw_outputs_path=raw_outputs_path,
        summary_path=summary_path,
        metadata_path=metadata_path,
    )


def _sanitize_id(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in value)
