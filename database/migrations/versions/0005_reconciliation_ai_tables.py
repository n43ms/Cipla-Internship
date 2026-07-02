"""reconciliation and ai tables

Revision ID: 0005_reconciliation_ai_tables
Revises: 0004_canonical_tables
Create Date: 2026-06-16
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0005_reconciliation_ai_tables"
down_revision: str | None = "0004_canonical_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def uuid_pk() -> sa.Column:
    return sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()"))


def upgrade() -> None:
    op.create_table(
        "event_matches",
        uuid_pk(),
        sa.Column("ingestion_run_id", sa.UUID(), sa.ForeignKey("ingestion_runs.id"), nullable=False),
        sa.Column("country_id", sa.UUID(), sa.ForeignKey("countries.id"), nullable=False),
        sa.Column("calendar_month_id", sa.UUID(), sa.ForeignKey("calendar_months.id"), nullable=False),
        sa.Column("plan_event_id", sa.UUID(), sa.ForeignKey("plan_events.id")),
        sa.Column("execution_snapshot_id", sa.UUID(), sa.ForeignKey("execution_snapshots.id")),
        sa.Column("execution_request_id", sa.UUID(), sa.ForeignKey("execution_requests.id")),
        sa.Column("match_method", sa.Text(), nullable=False),
        sa.Column("match_confidence", sa.Numeric(5, 4), nullable=False),
        sa.Column("match_status", sa.Text(), nullable=False),
        sa.Column("matched_on", sa.JSON()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "ai_query_logs",
        uuid_pk(),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("country_id", sa.UUID(), sa.ForeignKey("countries.id")),
        sa.Column("calendar_month_id", sa.UUID(), sa.ForeignKey("calendar_months.id")),
        sa.Column("question_redacted", sa.Text(), nullable=False),
        sa.Column("context_summary_json", sa.JSON(), nullable=False),
        sa.Column("answer", sa.Text()),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("model", sa.Text()),
        sa.Column("latency_ms", sa.Integer()),
        sa.Column("error_code", sa.Text()),
        sa.Column("error_message", sa.Text()),
    )


def downgrade() -> None:
    op.drop_table("ai_query_logs")
    op.drop_table("event_matches")
