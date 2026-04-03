"""TRIBE client interfaces and deterministic stub implementation."""

from __future__ import annotations

import hashlib
from typing import Protocol

from pydantic import BaseModel, Field

from echomind.tribe.preprocess import TribeStimulusInput


class TribeRawOutput(BaseModel):
    """Raw simulation artifact emitted per stimulus."""

    stimulus_id: str
    cue_id: str
    response_score: float
    token_count: int
    response_vector: list[float] = Field(default_factory=list)


class TribeClient(Protocol):
    """Wrapper boundary for TRIBE execution adapters."""

    def infer_batch(self, stimuli: list[TribeStimulusInput]) -> list[TribeRawOutput]:
        """Run simulation inference for preprocessed stimulus inputs."""


class StubTribeClient:
    """Deterministic stub used when real TRIBE runtime is unavailable."""

    def infer_batch(self, stimuli: list[TribeStimulusInput]) -> list[TribeRawOutput]:
        outputs: list[TribeRawOutput] = []

        for stimulus in stimuli:
            digest = hashlib.sha256(stimulus.text_input.encode("utf-8")).hexdigest()
            score_seed = int(digest[:8], 16)
            score = (score_seed % 10000) / 10000.0
            outputs.append(
                TribeRawOutput(
                    stimulus_id=stimulus.stimulus_id,
                    cue_id=stimulus.cue_id,
                    response_score=score,
                    token_count=len(stimulus.text_input.split()),
                    response_vector=[round(score, 4), round((score + 0.137) % 1.0, 4)],
                )
            )

        return outputs
