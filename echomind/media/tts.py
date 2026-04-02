"""Text-to-speech adapter contracts and deterministic stub implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class TTSAdapter(Protocol):
    """Pluggable text-to-speech adapter interface."""

    def synthesize(self, transcript: str, output_path: Path) -> Path:
        """Synthesize transcript to an audio artifact path."""


class StubTTSAdapter:
    """Deterministic TTS stub that writes a placeholder wav artifact."""

    def synthesize(self, transcript: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = (
            "STUB_WAV\n"
            f"transcript_length={len(transcript)}\n"
            f"transcript_preview={transcript[:120]}\n"
        )
        output_path.write_text(payload, encoding="utf-8")
        return output_path
