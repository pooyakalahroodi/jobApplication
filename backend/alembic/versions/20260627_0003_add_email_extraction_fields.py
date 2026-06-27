"""add email extraction fields

Revision ID: 20260627_0003
Revises: 20260627_0002
Create Date: 2026-06-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260627_0003"
down_revision: Union[str, None] = "20260627_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("emails", sa.Column("extracted_company", sa.String(), nullable=True))
    op.add_column("emails", sa.Column("extracted_role_title", sa.String(), nullable=True))
    op.add_column("emails", sa.Column("extraction_confidence", sa.Float(), nullable=True))
    op.create_index(op.f("ix_emails_extracted_company"), "emails", ["extracted_company"], unique=False)
    op.create_index(
        op.f("ix_emails_extracted_role_title"),
        "emails",
        ["extracted_role_title"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_emails_extracted_role_title"), table_name="emails")
    op.drop_index(op.f("ix_emails_extracted_company"), table_name="emails")
    op.drop_column("emails", "extraction_confidence")
    op.drop_column("emails", "extracted_role_title")
    op.drop_column("emails", "extracted_company")
