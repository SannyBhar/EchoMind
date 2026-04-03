"""Contract-first schemas for cue planning, stimulus manifests, and inference requests."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from echomind.db.enums import CueTone, PersonalizationLevel


class CueDeliveryMode(StrEnum):
    """Supported cue delivery structures for non-clinical simulation studies."""

    TEXT_ONLY = "text_only"
    NARRATION = "narration"
    SLIDESHOW_NARRATION = "slideshow_narration"


class InferenceStatus(StrEnum):
    """Execution status for simulation requests."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CueMetadataKey(StrEnum):
    """Recommended metadata keys for cue-planning traceability."""

    VARIANT_FAMILY = "variant_family"
    TEMPLATE_VERSION = "template_version"
    SEED = "seed"
    PLANNING_VERSION = "planning_version"
    PEOPLE_USED = "people_used"
    PLACE_USED = "place_used"


RECOMMENDED_METADATA_KEYS: tuple[str, ...] = tuple(item.value for item in CueMetadataKey)


class CueGenerationRequest(BaseModel):
    """Input contract for deterministic cue planning."""

    request_id: str
    memory_id: str
    memory_title: str
    memory_summary: str
    target_modes: list[CueDeliveryMode] = Field(min_length=1)
    max_variants_per_mode: int = Field(default=2, ge=1, le=5)
    include_people_context: bool = True
    include_place_context: bool = True
    seed: int = 0
    planning_version: str = "mvp.v1"


class CueVariantSpec(BaseModel):
    """Planned cue specification prior to media rendering."""

    cue_id: str
    memory_id: str
    delivery_mode: CueDeliveryMode
    tone: CueTone | str
    personalization_level: PersonalizationLevel | str
    script_text: str
    narration_text: str | None = None
    slide_image_prompts: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Recommended keys: variant_family, template_version, seed, "
            "planning_version, people_used, place_used"
        ),
    )

    @model_validator(mode="after")
    def validate_mode_fields(self) -> CueVariantSpec:
        """Enforce mode-specific field requirements."""

        if self.delivery_mode == CueDeliveryMode.TEXT_ONLY:
            if self.narration_text is not None or self.slide_image_prompts:
                msg = "text_only cues must not include narration or slideshow prompts"
                raise ValueError(msg)

        if self.delivery_mode == CueDeliveryMode.NARRATION:
            if not self.narration_text:
                msg = "narration cues require narration_text"
                raise ValueError(msg)
            if self.slide_image_prompts:
                msg = "narration cues must not include slideshow prompts"
                raise ValueError(msg)

        if self.delivery_mode == CueDeliveryMode.SLIDESHOW_NARRATION:
            if not self.narration_text:
                msg = "slideshow_narration cues require narration_text"
                raise ValueError(msg)
            if not self.slide_image_prompts:
                msg = "slideshow_narration cues require slide_image_prompts"
                raise ValueError(msg)

        return self


class RenderedStimulus(BaseModel):
    """Rendered or prepared stimulus payload for simulation requests."""

    stimulus_id: str
    cue_id: str
    delivery_mode: CueDeliveryMode
    text_payload: str | None = None
    narration_transcript: str | None = None
    narration_audio_uri: str | None = None
    slide_image_uris: list[str] = Field(default_factory=list)
    estimated_duration_sec: float | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Recommended keys: variant_family, template_version, seed, "
            "planning_version, people_used, place_used"
        ),
    )

    @model_validator(mode="after")
    def validate_rendered_shape(self) -> RenderedStimulus:
        """Ensure rendered payload shape matches delivery mode."""

        if self.delivery_mode == CueDeliveryMode.TEXT_ONLY:
            if not self.text_payload:
                raise ValueError("text_only stimulus requires text_payload")
            if self.narration_audio_uri or self.narration_transcript or self.slide_image_uris:
                raise ValueError(
                    "text_only stimulus must not include narration or slideshow payload"
                )

        if self.delivery_mode == CueDeliveryMode.NARRATION:
            if not self.narration_audio_uri and not self.narration_transcript:
                raise ValueError(
                    "narration stimulus requires narration_audio_uri or narration_transcript"
                )
            if self.slide_image_uris:
                raise ValueError("narration stimulus must not include slide_image_uris")

        if self.delivery_mode == CueDeliveryMode.SLIDESHOW_NARRATION:
            if not self.narration_audio_uri:
                raise ValueError("slideshow stimulus requires narration_audio_uri")
            if not self.slide_image_uris:
                raise ValueError("slideshow stimulus requires slide_image_uris")

        return self


class StimulusManifest(BaseModel):
    """Grouped stimulus payloads for one memory simulation batch."""

    manifest_id: str
    memory_id: str
    stimuli: list[RenderedStimulus] = Field(min_length=1)
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Recommended keys: variant_family, template_version, seed, "
            "planning_version, people_used, place_used"
        ),
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class InferenceRequest(BaseModel):
    """Contract sent to simulation infrastructure."""

    request_id: str
    engine_name: str = "tribe-v2"
    stimulus_manifest: StimulusManifest
    include_raw_artifacts: bool = False


class InferenceResultSummary(BaseModel):
    """Top-level summary artifact for non-clinical simulation output."""

    request_id: str
    engine_name: str
    status: InferenceStatus
    ranked_cue_ids: list[str] = Field(default_factory=list)
    aggregate_scores: dict[str, float] = Field(default_factory=dict)
    summary_metadata: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
