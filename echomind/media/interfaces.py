"""Media rendering interface placeholders."""

from typing import Protocol


class MediaRenderer(Protocol):
    """Contract for rendering cue variants into multimodal stimuli."""

    def render(self, cue_payload: dict[str, str]) -> dict[str, str]:
        """Return references to rendered text/audio/video stimuli assets."""
