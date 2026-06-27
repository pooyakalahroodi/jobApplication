"""add browser capture fields

Revision ID: 20260627_0002
Revises: 20260627_0001
Create Date: 2026-06-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260627_0002"
down_revision: Union[str, None] = "20260627_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("job_ads", sa.Column("source", sa.String(), nullable=True))
    op.add_column("job_ads", sa.Column("page_title", sa.String(), nullable=True))
    op.add_column("job_ads", sa.Column("selected_text", sa.Text(), nullable=True))
    op.add_column("job_ads", sa.Column("raw_text", sa.Text(), nullable=True))
    op.add_column("job_ads", sa.Column("json_ld", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("job_ads", "json_ld")
    op.drop_column("job_ads", "raw_text")
    op.drop_column("job_ads", "selected_text")
    op.drop_column("job_ads", "page_title")
    op.drop_column("job_ads", "source")

