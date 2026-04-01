"""SQLAlchemy ORM entities for MVP persistence contracts."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from remembra.db.base import Base
from remembra.db.enums import (
    AssetType,
    CueTone,
    CueType,
    JobStatus,
    MemoryType,
    PersonalizationLevel,
)

memory_people = Table(
    "memory_people",
    Base.metadata,
    Column("memory_id", ForeignKey("memories.id", ondelete="CASCADE"), primary_key=True),
    Column("person_id", ForeignKey("people.id", ondelete="CASCADE"), primary_key=True),
)


class Place(Base):
    """Location metadata attached to autobiographical memories."""

    __tablename__ = "places"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    memories: Mapped[list[Memory]] = relationship(back_populates="place")


class Person(Base):
    """Person metadata associated with memories."""

    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    memories: Mapped[list[Memory]] = relationship(
        secondary=memory_people,
        back_populates="people",
    )


class Memory(Base):
    """Core autobiographical memory record used in in-silico experiments."""

    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    narrative: Mapped[str] = mapped_column(Text, nullable=False)
    memory_type: Mapped[MemoryType] = mapped_column(
        Enum(MemoryType, name="memory_type_enum", native_enum=False), nullable=False
    )
    event_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    place_id: Mapped[int | None] = mapped_column(ForeignKey("places.id", ondelete="SET NULL"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    place: Mapped[Place | None] = relationship(back_populates="memories")
    people: Mapped[list[Person]] = relationship(
        secondary=memory_people,
        back_populates="memories",
    )
    assets: Mapped[list[Asset]] = relationship(
        back_populates="memory", cascade="all, delete-orphan", passive_deletes=True
    )
    cue_variants: Mapped[list[CueVariant]] = relationship(
        back_populates="memory", cascade="all, delete-orphan", passive_deletes=True
    )


class Asset(Base):
    """External media assets linked to a memory record."""

    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    memory_id: Mapped[int] = mapped_column(
        ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    asset_type: Mapped[AssetType] = mapped_column(
        Enum(AssetType, name="asset_type_enum", native_enum=False), nullable=False
    )
    uri: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    memory: Mapped[Memory] = relationship(back_populates="assets")


class CueVariant(Base):
    """Candidate cue variant generated for simulation-based comparison."""

    __tablename__ = "cue_variants"
    __table_args__ = (
        UniqueConstraint(
            "memory_id",
            "cue_type",
            "tone",
            "personalization_level",
            name="uq_cue_variant_design",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    memory_id: Mapped[int] = mapped_column(
        ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cue_type: Mapped[CueType] = mapped_column(
        Enum(CueType, name="cue_type_enum", native_enum=False), nullable=False
    )
    tone: Mapped[CueTone] = mapped_column(
        Enum(CueTone, name="cue_tone_enum", native_enum=False), nullable=False
    )
    personalization_level: Mapped[PersonalizationLevel] = mapped_column(
        Enum(PersonalizationLevel, name="personalization_level_enum", native_enum=False),
        nullable=False,
    )
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    memory: Mapped[Memory] = relationship(back_populates="cue_variants")
    inference_runs: Mapped[list[InferenceRun]] = relationship(
        back_populates="cue_variant", cascade="all, delete-orphan", passive_deletes=True
    )


class InferenceRun(Base):
    """Simulation execution metadata for one cue variant."""

    __tablename__ = "inference_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cue_variant_id: Mapped[int] = mapped_column(
        ForeignKey("cue_variants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status_enum", native_enum=False),
        nullable=False,
        default=JobStatus.PENDING,
    )
    engine_name: Mapped[str] = mapped_column(String(128), nullable=False, default="tribe-v2")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    cue_variant: Mapped[CueVariant] = relationship(back_populates="inference_runs")
    score_outputs: Mapped[list[ScoreOutput]] = relationship(
        back_populates="inference_run", cascade="all, delete-orphan", passive_deletes=True
    )


class ScoreOutput(Base):
    """Structured score components emitted for a simulation run."""

    __tablename__ = "score_outputs"
    __table_args__ = (UniqueConstraint("inference_run_id", "metric_name", name="uq_run_metric"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inference_run_id: Mapped[int] = mapped_column(
        ForeignKey("inference_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    metric_name: Mapped[str] = mapped_column(String(120), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    details_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    inference_run: Mapped[InferenceRun] = relationship(back_populates="score_outputs")
