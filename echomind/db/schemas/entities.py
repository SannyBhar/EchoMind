"""Pydantic v2 schemas for persistence-facing API contracts."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from echomind.db.enums import (
    AssetType,
    CueTone,
    CueType,
    JobStatus,
    MemoryType,
    PersonalizationLevel,
)


class ORMModel(BaseModel):
    """Base schema with SQLAlchemy attribute support."""

    model_config = ConfigDict(from_attributes=True)


class PersonCreate(BaseModel):
    full_name: str
    notes: str | None = None


class PersonRead(ORMModel):
    id: int
    full_name: str
    notes: str | None
    created_at: datetime
    updated_at: datetime


class PlaceCreate(BaseModel):
    name: str
    description: str | None = None


class PlaceRead(ORMModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class AssetCreate(BaseModel):
    memory_id: int
    asset_type: AssetType
    uri: str
    description: str | None = None


class AssetRead(ORMModel):
    id: int
    memory_id: int
    asset_type: AssetType
    uri: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class MemoryCreate(BaseModel):
    external_id: str
    title: str
    narrative: str
    memory_type: MemoryType
    event_date: date | None = None
    place_id: int | None = None


class CueVariantCreate(BaseModel):
    memory_id: int
    cue_type: CueType
    tone: CueTone
    personalization_level: PersonalizationLevel
    prompt_text: str


class CueVariantRead(ORMModel):
    id: int
    memory_id: int
    cue_type: CueType
    tone: CueTone
    personalization_level: PersonalizationLevel
    prompt_text: str
    created_at: datetime
    updated_at: datetime


class InferenceRunCreate(BaseModel):
    cue_variant_id: int
    status: JobStatus = JobStatus.PENDING
    engine_name: str = "tribe-v2"


class InferenceRunRead(ORMModel):
    id: int
    cue_variant_id: int
    status: JobStatus
    engine_name: str
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ScoreOutputCreate(BaseModel):
    inference_run_id: int
    metric_name: str
    metric_value: float
    details_json: dict[str, float | str] | None = None


class ScoreOutputRead(ORMModel):
    id: int
    inference_run_id: int
    metric_name: str
    metric_value: float
    details_json: dict[str, float | str] | None
    created_at: datetime


class MemoryRead(ORMModel):
    id: int
    external_id: str
    title: str
    narrative: str
    memory_type: MemoryType
    event_date: date | None
    place: PlaceRead | None
    people: list[PersonRead]
    assets: list[AssetRead]
    cue_variants: list[CueVariantRead]
    created_at: datetime
    updated_at: datetime
