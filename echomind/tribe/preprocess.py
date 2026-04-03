"""Preprocessing utilities mapping EchoMind stimuli to TRIBE-compatible payloads."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from echomind.cues.contracts import CueDeliveryMode, StimulusManifest


class TribeStimulusInput(BaseModel):
    """Normalized stimulus payload consumed by TRIBE integration adapters."""

    stimulus_id: str
    cue_id: str
    modality: CueDeliveryMode
    text_input: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class TribeBatchInput(BaseModel):
    """Batch payload prepared for one TRIBE simulation request."""

    request_id: str
    memory_id: str
    engine_name: str
    stimuli: list[TribeStimulusInput]
    metadata: dict[str, Any] = Field(default_factory=dict)


def preprocess_manifest_for_tribe(
    manifest: StimulusManifest,
    request_id: str,
    engine_name: str = "tribe-v2",
    supported_modalities: set[CueDeliveryMode] | None = None,
) -> TribeBatchInput:
    """Convert rendered stimuli into TRIBE-ready deterministic batch payloads."""

    allowed_modalities = supported_modalities or {CueDeliveryMode.TEXT_ONLY}

    preprocessed: list[TribeStimulusInput] = []
    for stimulus in manifest.stimuli:
        if stimulus.delivery_mode not in allowed_modalities:
            continue

        text_input = _to_text_input(stimulus)
        preprocessed.append(
            TribeStimulusInput(
                stimulus_id=stimulus.stimulus_id,
                cue_id=stimulus.cue_id,
                modality=stimulus.delivery_mode,
                text_input=text_input,
                metadata=stimulus.metadata,
            )
        )

    return TribeBatchInput(
        request_id=request_id,
        memory_id=manifest.memory_id,
        engine_name=engine_name,
        stimuli=preprocessed,
        metadata=manifest.metadata,
    )


def _to_text_input(stimulus) -> str:
    """Build a deterministic text representation for TRIBE adapters."""

    if stimulus.delivery_mode == CueDeliveryMode.TEXT_ONLY:
        return stimulus.text_payload or ""

    if stimulus.delivery_mode == CueDeliveryMode.NARRATION:
        return stimulus.narration_transcript or ""

    if stimulus.delivery_mode == CueDeliveryMode.SLIDESHOW_NARRATION:
        return stimulus.narration_transcript or ""

    return ""
