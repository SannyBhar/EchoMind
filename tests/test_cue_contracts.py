from echomind.cues.contracts import (
    CueDeliveryMode,
    CueGenerationRequest,
    CueVariantSpec,
    InferenceRequest,
    InferenceResultSummary,
    RenderedStimulus,
    StimulusManifest,
)
from echomind.cues.contracts_service import (
    build_inference_request,
    build_stimulus_manifest,
    plan_cue_variants,
    summarize_placeholder_inference,
)


def test_contract_examples_cover_text_narration_and_slideshow() -> None:
    request = CueGenerationRequest(
        request_id="req-001",
        memory_id="demo-memory-001",
        memory_title="First Day at University",
        memory_summary="Walked campus and found lecture hall with friends.",
        target_modes=[
            CueDeliveryMode.TEXT_ONLY,
            CueDeliveryMode.NARRATION,
            CueDeliveryMode.SLIDESHOW_NARRATION,
        ],
    )

    variants = plan_cue_variants(request)
    manifest = build_stimulus_manifest(request.memory_id, variants)

    assert len(variants) == 3
    assert variants[0].delivery_mode == CueDeliveryMode.TEXT_ONLY
    assert variants[1].delivery_mode == CueDeliveryMode.NARRATION
    assert variants[2].delivery_mode == CueDeliveryMode.SLIDESHOW_NARRATION

    assert len(manifest.stimuli) == 3
    assert manifest.stimuli[0].text_payload is not None
    assert manifest.stimuli[1].narration_audio_uri is not None
    assert len(manifest.stimuli[2].slide_image_uris) == 3


def test_schema_serialization_round_trip() -> None:
    stimulus = RenderedStimulus(
        stimulus_id="stim-001",
        cue_id="cue-001",
        delivery_mode=CueDeliveryMode.NARRATION,
        narration_transcript="Narration transcript",
        narration_audio_uri="memory://audio/cue-001.wav",
    )
    manifest = StimulusManifest(
        manifest_id="manifest-001",
        memory_id="demo-memory-001",
        stimuli=[stimulus],
    )
    request = InferenceRequest(
        request_id="inference-001",
        engine_name="tribe-v2",
        stimulus_manifest=manifest,
    )

    payload = request.model_dump(mode="json")
    restored = InferenceRequest.model_validate(payload)

    assert restored.request_id == "inference-001"
    assert restored.stimulus_manifest.stimuli[0].cue_id == "cue-001"


def test_placeholder_inference_summary_contract() -> None:
    variant = CueVariantSpec(
        cue_id="cue-xyz",
        memory_id="demo-memory-001",
        delivery_mode=CueDeliveryMode.TEXT_ONLY,
        tone="neutral",
        personalization_level="medium",
        script_text="Recall campus path.",
    )
    manifest = build_stimulus_manifest("demo-memory-001", [variant])
    request = build_inference_request(manifest)
    summary = summarize_placeholder_inference(request)

    assert isinstance(summary, InferenceResultSummary)
    assert summary.status == "pending"
    assert summary.ranked_cue_ids == ["cue-xyz"]
