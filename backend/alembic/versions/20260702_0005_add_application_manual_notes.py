"""add application manual notes

Revision ID: 20260702_0005
Revises: 20260627_0004
Create Date: 2026-07-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260702_0005"
down_revision: Union[str, None] = "20260627_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("applications", sa.Column("manual_notes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("applications", "manual_notes")
