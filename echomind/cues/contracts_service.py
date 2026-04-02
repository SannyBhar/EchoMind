"""Deterministic placeholder services for cue/stimulus/inference contracts."""

from __future__ import annotations

from echomind.cues.contracts import (
    CueDeliveryMode,
    CueGenerationRequest,
    CueMetadataKey,
    CueVariantSpec,
    InferenceRequest,
    InferenceResultSummary,
    InferenceStatus,
    RenderedStimulus,
    StimulusManifest,
)


def plan_cue_variants(request: CueGenerationRequest) -> list[CueVariantSpec]:
    """Create deterministic placeholder cue variants from request contracts."""

    variants: list[CueVariantSpec] = []

    for idx, mode in enumerate(request.target_modes, start=1):
        cue_id = f"{request.memory_id}-cue-{idx}"
        base_text = f"Cue for {request.memory_title}: {request.memory_summary}"

        if mode == CueDeliveryMode.TEXT_ONLY:
            variants.append(
                CueVariantSpec(
                    cue_id=cue_id,
                    memory_id=request.memory_id,
                    delivery_mode=mode,
                    tone="neutral",
                    personalization_level="medium",
                    script_text=base_text,
                    metadata={
                        CueMetadataKey.VARIANT_FAMILY.value: "placeholder",
                        CueMetadataKey.TEMPLATE_VERSION.value: "placeholder.v1",
                        CueMetadataKey.SEED.value: request.seed,
                        CueMetadataKey.PLANNING_VERSION.value: request.planning_version,
                        CueMetadataKey.PEOPLE_USED.value: [],
                        CueMetadataKey.PLACE_USED.value: None,
                    },
                )
            )
        elif mode == CueDeliveryMode.NARRATION:
            variants.append(
                CueVariantSpec(
                    cue_id=cue_id,
                    memory_id=request.memory_id,
                    delivery_mode=mode,
                    tone="warm",
                    personalization_level="high",
                    script_text=base_text,
                    narration_text=f"Narrate: {base_text}",
                    metadata={
                        CueMetadataKey.VARIANT_FAMILY.value: "placeholder",
                        CueMetadataKey.TEMPLATE_VERSION.value: "placeholder.v1",
                        CueMetadataKey.SEED.value: request.seed,
                        CueMetadataKey.PLANNING_VERSION.value: request.planning_version,
                        CueMetadataKey.PEOPLE_USED.value: [],
                        CueMetadataKey.PLACE_USED.value: None,
                    },
                )
            )
        else:
            variants.append(
                CueVariantSpec(
                    cue_id=cue_id,
                    memory_id=request.memory_id,
                    delivery_mode=mode,
                    tone="vivid",
                    personalization_level="high",
                    script_text=base_text,
                    narration_text=f"Narrate slideshow for {request.memory_title}",
                    slide_image_prompts=[
                        "establishing memory context frame",
                        "key people and place frame",
                        "closing reflection frame",
                    ],
                    metadata={
                        CueMetadataKey.VARIANT_FAMILY.value: "placeholder",
                        CueMetadataKey.TEMPLATE_VERSION.value: "placeholder.v1",
                        CueMetadataKey.SEED.value: request.seed,
                        CueMetadataKey.PLANNING_VERSION.value: request.planning_version,
                        CueMetadataKey.PEOPLE_USED.value: [],
                        CueMetadataKey.PLACE_USED.value: None,
                    },
                )
            )

    return variants


def build_stimulus_manifest(memory_id: str, variants: list[CueVariantSpec]) -> StimulusManifest:
    """Build deterministic rendered-stimulus placeholders for simulation requests."""

    stimuli: list[RenderedStimulus] = []
    for variant in variants:
        if variant.delivery_mode == CueDeliveryMode.TEXT_ONLY:
            stimuli.append(
                RenderedStimulus(
                    stimulus_id=f"{variant.cue_id}-stimulus",
                    cue_id=variant.cue_id,
                    delivery_mode=variant.delivery_mode,
                    text_payload=variant.script_text,
                )
            )
        elif variant.delivery_mode == CueDeliveryMode.NARRATION:
            stimuli.append(
                RenderedStimulus(
                    stimulus_id=f"{variant.cue_id}-stimulus",
                    cue_id=variant.cue_id,
                    delivery_mode=variant.delivery_mode,
                    narration_transcript=variant.narration_text,
                    narration_audio_uri=f"memory://audio/{variant.cue_id}.wav",
                )
            )
        else:
            stimuli.append(
                RenderedStimulus(
                    stimulus_id=f"{variant.cue_id}-stimulus",
                    cue_id=variant.cue_id,
                    delivery_mode=variant.delivery_mode,
                    narration_transcript=variant.narration_text,
                    narration_audio_uri=f"memory://audio/{variant.cue_id}.wav",
                    slide_image_uris=[
                        f"memory://slides/{variant.cue_id}/1.png",
                        f"memory://slides/{variant.cue_id}/2.png",
                        f"memory://slides/{variant.cue_id}/3.png",
                    ],
                )
            )

    return StimulusManifest(
        manifest_id=f"manifest-{memory_id}",
        memory_id=memory_id,
        stimuli=stimuli,
    )


def build_inference_request(manifest: StimulusManifest) -> InferenceRequest:
    """Build simulation request contract from a prepared manifest."""

    return InferenceRequest(
        request_id=f"inference-{manifest.memory_id}",
        engine_name="tribe-v2",
        stimulus_manifest=manifest,
    )


def summarize_placeholder_inference(request: InferenceRequest) -> InferenceResultSummary:
    """Return placeholder summary without running simulation logic."""

    ranked_cues = [stimulus.cue_id for stimulus in request.stimulus_manifest.stimuli]
    return InferenceResultSummary(
        request_id=request.request_id,
        engine_name=request.engine_name,
        status=InferenceStatus.PENDING,
        ranked_cue_ids=ranked_cues,
        aggregate_scores={},
        notes="Placeholder summary for in-silico pipeline wiring.",
    )
