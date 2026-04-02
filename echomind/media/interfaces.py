"""Media rendering interfaces for deterministic MVP outputs."""

from __future__ import annotations

from typing import Protocol

from echomind.cues.contracts import CueVariantSpec, RenderedStimulus, StimulusManifest


class MediaRenderer(Protocol):
    """Contract for rendering cue variants into deterministic stimuli."""

    def render_variant(self, variant: CueVariantSpec) -> RenderedStimulus:
        """Render one cue variant into a validated stimulus artifact."""

    def render_manifest(
        self,
        memory_id: str,
        variants: list[CueVariantSpec],
        manifest_id: str | None = None,
    ) -> StimulusManifest:
        """Render a cue family into a deterministic manifest."""
