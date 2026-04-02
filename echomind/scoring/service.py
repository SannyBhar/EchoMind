"""Score-output persistence services."""

from __future__ import annotations

from sqlalchemy.orm import Session

from echomind.db.models import ScoreOutput
from echomind.db.schemas import ScoreOutputCreate


def create_score_output(session: Session, payload: ScoreOutputCreate) -> ScoreOutput:
    """Create and persist one score output component."""

    score = ScoreOutput(**payload.model_dump())
    session.add(score)
    session.flush()
    return score
