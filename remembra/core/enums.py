"""Shared enums for high-level domain vocabulary."""

from enum import StrEnum


class CueModality(StrEnum):
    """Supported cue modality families for future expansion."""

    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
