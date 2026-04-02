"""Deterministic artifact path and manifest helpers for media rendering."""

from __future__ import annotations

from pathlib import Path

RENDER_VERSION = "mvp.render.v1"


def ensure_artifact_root(path: str | Path) -> Path:
    """Create and return a deterministic artifact root path."""

    root = Path(path)
    root.mkdir(parents=True, exist_ok=True)
    return root


def cue_artifact_dir(artifact_root: Path, memory_id: str, cue_id: str) -> Path:
    """Return deterministic artifact directory for a cue variant."""

    path = artifact_root / sanitize_id(memory_id) / sanitize_id(cue_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def sanitize_id(value: str) -> str:
    """Sanitize IDs for stable filesystem paths."""

    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in value)
