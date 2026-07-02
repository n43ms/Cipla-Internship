"""budget finance view

Revision ID: 0016_budget_finance_view
Revises: 0015_snapshot_provenance
Create Date: 2026-06-19
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0016_budget_finance_view"
down_revision: str | None = "0015_snapshot_provenance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("drop materialized view if exists mv_budget_utilization")
    op.execute(_read_view_sql("mv_budget_utilization.sql"))
    op.create_index("ix_mv_budget_utilization_country_month", "mv_budget_utilization", ["country_id", "calendar_month_id"])
    op.create_index("ix_mv_budget_utilization_scope", "mv_budget_utilization", ["is_primary_phase4_scope"])
    op.create_index("ix_mv_budget_utilization_match_status", "mv_budget_utilization", ["match_status"])
    op.create_index("ix_execution_requests_finance_country_month", "execution_requests", ["country_id", "calendar_month_id"])
    op.create_index("ix_execution_requests_fx_status", "execution_requests", ["fx_rate_status"])
    op.execute("refresh materialized view mv_budget_utilization")


def downgrade() -> None:
    op.drop_index("ix_execution_requests_fx_status", table_name="execution_requests")
    op.drop_index("ix_execution_requests_finance_country_month", table_name="execution_requests")
    op.drop_index("ix_mv_budget_utilization_match_status", table_name="mv_budget_utilization")
    op.drop_index("ix_mv_budget_utilization_scope", table_name="mv_budget_utilization")
    op.drop_index("ix_mv_budget_utilization_country_month", table_name="mv_budget_utilization")
    op.execute("drop materialized view if exists mv_budget_utilization")


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(encoding="utf-8")
