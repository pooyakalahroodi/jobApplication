"""add extraction runs

Revision ID: 20260627_0004
Revises: 20260627_0003
Create Date: 2026-06-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260627_0004"
down_revision: Union[str, None] = "20260627_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "extraction_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "source_type",
            sa.Enum("email", "job_ad", name="extractionsourcetype"),
            nullable=False,
        ),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("extractor", sa.String(), nullable=False),
        sa.Column("model", sa.String(), nullable=True),
        sa.Column("prompt_version", sa.String(), nullable=False),
        sa.Column("raw_input_hash", sa.String(), nullable=False),
        sa.Column("raw_output", sa.Text(), nullable=True),
        sa.Column("parsed_json", sa.JSON(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("success", "failed", name="extractionstatus"),
            nullable=False,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_extraction_runs_id"), "extraction_runs", ["id"], unique=False)
    op.create_index(
        op.f("ix_extraction_runs_source_id"),
        "extraction_runs",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_extraction_runs_source_type"),
        "extraction_runs",
        ["source_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_extraction_runs_source_type"), table_name="extraction_runs")
    op.drop_index(op.f("ix_extraction_runs_source_id"), table_name="extraction_runs")
    op.drop_index(op.f("ix_extraction_runs_id"), table_name="extraction_runs")
    op.drop_table("extraction_runs")
