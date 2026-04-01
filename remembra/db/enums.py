"""Database-backed enums for Remembra persistence contracts."""

from enum import StrEnum


class MemoryType(StrEnum):
    """Supported autobiographical memory categories."""

    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class AssetType(StrEnum):
    """Supported source asset modalities."""

    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"


class CueType(StrEnum):
    """Cue variant families for simulation-based comparison."""

    TEXT_PROMPT = "text_prompt"
    AUDIO_PROMPT = "audio_prompt"
    VIDEO_PROMPT = "video_prompt"


class CueTone(StrEnum):
    """Cue tone labels used for variant diversification."""

    NEUTRAL = "neutral"
    WARM = "warm"
    VIVID = "vivid"


class PersonalizationLevel(StrEnum):
    """Personalization depth for candidate cue variants."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class JobStatus(StrEnum):
    """Background job status for simulation pipeline steps."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
