"""phase 4 execution matrix and KPI fixes

Revision ID: 0011_phase4_matrix_fixes
Revises: 0010_execution_governance_views
Create Date: 2026-06-17
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0011_phase4_matrix_fixes"
down_revision: str | None = "0010_execution_governance_views"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("drop index if exists ix_mv_execution_kpis_country_month")
    op.execute("drop materialized view if exists mv_execution_kpis")
    op.execute(_read_view_sql("mv_execution_kpis.sql"))
    op.create_index("ix_mv_execution_kpis_country_month", "mv_execution_kpis", ["country_id", "calendar_month_id"])

    op.execute(_read_view_sql("mv_execution_event_matrix.sql"))
    op.create_index(
        "ix_mv_execution_event_matrix_country_month",
        "mv_execution_event_matrix",
        ["country_id", "calendar_month_id"],
    )
    op.create_index("ix_mv_execution_event_matrix_status", "mv_execution_event_matrix", ["match_status"])

    op.execute(_read_view_sql("refresh_materialized_views.sql"))


def downgrade() -> None:
    op.drop_index("ix_mv_execution_event_matrix_status", table_name="mv_execution_event_matrix")
    op.drop_index("ix_mv_execution_event_matrix_country_month", table_name="mv_execution_event_matrix")
    op.execute("drop materialized view if exists mv_execution_event_matrix")

    op.execute("drop index if exists ix_mv_execution_kpis_country_month")
    op.execute("drop materialized view if exists mv_execution_kpis")
    op.execute(
        """
        create materialized view if not exists mv_execution_kpis as
        select
            null::uuid as country_id,
            null::text as country_code,
            null::text as country_name,
            null::uuid as calendar_month_id,
            null::date as month_start_date,
            null::text as month_label,
            0::bigint as planned_events,
            0::bigint as matched_events,
            0::bigint as weak_or_unmatched_events,
            0::bigint as executed_events,
            0::bigint as action_due_events,
            0::integer as planned_hcps,
            0::integer as engaged_hcps,
            0::numeric as hcp_execution_rate,
            0::numeric as event_execution_rate,
            0::numeric as match_coverage,
            '{}'::jsonb as snapshot_source_counts,
            now() as refreshed_at
        where false
        """
    )
    op.create_index("ix_mv_execution_kpis_country_month", "mv_execution_kpis", ["country_id", "calendar_month_id"])


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(encoding="utf-8")
