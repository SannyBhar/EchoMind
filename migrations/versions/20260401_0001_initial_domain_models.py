"""create initial domain models

Revision ID: 20260401_0001
Revises:
Create Date: 2026-04-01 19:30:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260401_0001"
down_revision = None
branch_labels = None
depends_on = None


memory_type_enum = sa.Enum("episodic", "semantic", name="memory_type_enum", native_enum=False)
asset_type_enum = sa.Enum(
    "image", "audio", "video", "text", name="asset_type_enum", native_enum=False
)
cue_type_enum = sa.Enum(
    "text_prompt",
    "audio_prompt",
    "video_prompt",
    name="cue_type_enum",
    native_enum=False,
)
cue_tone_enum = sa.Enum("neutral", "warm", "vivid", name="cue_tone_enum", native_enum=False)
personalization_level_enum = sa.Enum(
    "low",
    "medium",
    "high",
    name="personalization_level_enum",
    native_enum=False,
)
job_status_enum = sa.Enum(
    "pending",
    "running",
    "succeeded",
    "failed",
    name="job_status_enum",
    native_enum=False,
)


def upgrade() -> None:
    """Apply initial domain tables and constraints."""

    op.create_table(
        "people",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("full_name"),
    )

    op.create_table(
        "places",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "memories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("external_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("narrative", sa.Text(), nullable=False),
        sa.Column("memory_type", memory_type_enum, nullable=False),
        sa.Column("event_date", sa.Date(), nullable=True),
        sa.Column("place_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["place_id"], ["places.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id"),
    )
    op.create_index("ix_memories_external_id", "memories", ["external_id"], unique=False)

    op.create_table(
        "memory_people",
        sa.Column("memory_id", sa.Integer(), nullable=False),
        sa.Column("person_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["memory_id"], ["memories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["person_id"], ["people.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("memory_id", "person_id"),
    )

    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("memory_id", sa.Integer(), nullable=False),
        sa.Column("asset_type", asset_type_enum, nullable=False),
        sa.Column("uri", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["memory_id"], ["memories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_assets_memory_id", "assets", ["memory_id"], unique=False)

    op.create_table(
        "cue_variants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("memory_id", sa.Integer(), nullable=False),
        sa.Column("cue_type", cue_type_enum, nullable=False),
        sa.Column("tone", cue_tone_enum, nullable=False),
        sa.Column("personalization_level", personalization_level_enum, nullable=False),
        sa.Column("prompt_text", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["memory_id"], ["memories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "memory_id",
            "cue_type",
            "tone",
            "personalization_level",
            name="uq_cue_variant_design",
        ),
    )
    op.create_index("ix_cue_variants_memory_id", "cue_variants", ["memory_id"], unique=False)

    op.create_table(
        "inference_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cue_variant_id", sa.Integer(), nullable=False),
        sa.Column("status", job_status_enum, nullable=False),
        sa.Column("engine_name", sa.String(length=128), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["cue_variant_id"], ["cue_variants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_inference_runs_cue_variant_id", "inference_runs", ["cue_variant_id"], unique=False
    )

    op.create_table(
        "score_outputs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("inference_run_id", sa.Integer(), nullable=False),
        sa.Column("metric_name", sa.String(length=120), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("details_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["inference_run_id"], ["inference_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("inference_run_id", "metric_name", name="uq_run_metric"),
    )
    op.create_index(
        "ix_score_outputs_inference_run_id", "score_outputs", ["inference_run_id"], unique=False
    )


def downgrade() -> None:
    """Rollback initial domain tables and constraints."""

    op.drop_index("ix_score_outputs_inference_run_id", table_name="score_outputs")
    op.drop_table("score_outputs")

    op.drop_index("ix_inference_runs_cue_variant_id", table_name="inference_runs")
    op.drop_table("inference_runs")

    op.drop_index("ix_cue_variants_memory_id", table_name="cue_variants")
    op.drop_table("cue_variants")

    op.drop_index("ix_assets_memory_id", table_name="assets")
    op.drop_table("assets")

    op.drop_table("memory_people")

    op.drop_index("ix_memories_external_id", table_name="memories")
    op.drop_table("memories")

    op.drop_table("places")
    op.drop_table("people")
