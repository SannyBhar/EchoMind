"""Cue and inference persistence services."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from echomind.db.models import CueVariant, InferenceRun
from echomind.db.schemas import CueVariantCreate, InferenceRunCreate


def create_cue_variant(session: Session, payload: CueVariantCreate) -> CueVariant:
    """Create and persist a cue variant."""

    variant = CueVariant(**payload.model_dump())
    session.add(variant)
    session.flush()
    return variant


def list_cue_variants_for_memory(session: Session, memory_id: int) -> list[CueVariant]:
    """List cue variants for a memory."""

    stmt = select(CueVariant).where(CueVariant.memory_id == memory_id).order_by(CueVariant.id)
    return list(session.scalars(stmt).all())


def create_inference_run(session: Session, payload: InferenceRunCreate) -> InferenceRun:
    """Create and persist an inference run record."""

    inference_run = InferenceRun(**payload.model_dump())
    session.add(inference_run)
    session.flush()
    return inference_run
