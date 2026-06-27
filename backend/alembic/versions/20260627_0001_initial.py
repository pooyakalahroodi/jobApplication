"""initial schema

Revision ID: 20260627_0001
Revises:
Create Date: 2026-06-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260627_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "job_ads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("company", sa.String(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("not_applied", "applied", "rejected", "accepted", "archived", name="jobadstatus"),
            nullable=False,
        ),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_job_ads_id"), "job_ads", ["id"], unique=False)
    op.create_index(op.f("ix_job_ads_title"), "job_ads", ["title"], unique=False)
    op.create_index(op.f("ix_job_ads_company"), "job_ads", ["company"], unique=False)

    op.create_table(
        "emails",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("sender", sa.String(), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "email_status",
            sa.Enum("pending", "rejected", "accepted", "unknown", name="emailstatus"),
            nullable=False,
        ),
        sa.Column(
            "match_status",
            sa.Enum("not_set", "set", "needs_review", name="matchstatus"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_emails_id"), "emails", ["id"], unique=False)
    op.create_index(op.f("ix_emails_subject"), "emails", ["subject"], unique=False)
    op.create_index(op.f("ix_emails_sender"), "emails", ["sender"], unique=False)

    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_ad_id", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("applied", "pending", "rejected", "accepted", "unknown", name="applicationstatus"),
            nullable=False,
        ),
        sa.Column("company", sa.String(), nullable=True),
        sa.Column("role_title", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["job_ad_id"], ["job_ads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_applications_id"), "applications", ["id"], unique=False)
    op.create_index(op.f("ix_applications_company"), "applications", ["company"], unique=False)
    op.create_index(op.f("ix_applications_role_title"), "applications", ["role_title"], unique=False)

    op.create_table(
        "application_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("email_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("event_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"]),
        sa.ForeignKeyConstraint(["email_id"], ["emails.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_application_events_id"), "application_events", ["id"], unique=False)
    op.create_index(
        op.f("ix_application_events_event_type"),
        "application_events",
        ["event_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_application_events_event_type"), table_name="application_events")
    op.drop_index(op.f("ix_application_events_id"), table_name="application_events")
    op.drop_table("application_events")
    op.drop_index(op.f("ix_applications_role_title"), table_name="applications")
    op.drop_index(op.f("ix_applications_company"), table_name="applications")
    op.drop_index(op.f("ix_applications_id"), table_name="applications")
    op.drop_table("applications")
    op.drop_index(op.f("ix_emails_sender"), table_name="emails")
    op.drop_index(op.f("ix_emails_subject"), table_name="emails")
    op.drop_index(op.f("ix_emails_id"), table_name="emails")
    op.drop_table("emails")
    op.drop_index(op.f("ix_job_ads_company"), table_name="job_ads")
    op.drop_index(op.f("ix_job_ads_title"), table_name="job_ads")
    op.drop_index(op.f("ix_job_ads_id"), table_name="job_ads")
    op.drop_table("job_ads")

