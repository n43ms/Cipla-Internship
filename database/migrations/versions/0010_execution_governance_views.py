"""execution governance materialized views

Revision ID: 0010_execution_governance_views
Revises: 0009_drop_rcpa_prescriptions
Create Date: 2026-06-17
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0010_execution_governance_views"
down_revision: str | None = "0009_drop_rcpa_prescriptions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


VIEW_FILES = [
    "mv_execution_kpis.sql",
    "mv_unmatched_events.sql",
    "mv_workflow_governance.sql",
    "mv_intervention_mix.sql",
]


def upgrade() -> None:
    op.execute("alter table event_matches add column if not exists unmatched_reason_code text")
    op.execute("alter table event_matches add column if not exists unmatched_reason_detail text")
    op.execute(_read_view_sql("phase4_analysis_scope.sql"))
    for view_file in VIEW_FILES:
        op.execute(_read_view_sql(view_file))
    op.create_index("ix_mv_execution_kpis_country_month", "mv_execution_kpis", ["country_id", "calendar_month_id"])
    op.create_index("ix_mv_unmatched_events_country_month", "mv_unmatched_events", ["country_id", "calendar_month_id"])
    op.create_index("ix_mv_workflow_governance_country_month", "mv_workflow_governance", ["country_id", "calendar_month_id"])
    op.create_index("ix_mv_intervention_mix_country_month", "mv_intervention_mix", ["country_id", "calendar_month_id"])
    op.create_index("ix_event_matches_status", "event_matches", ["match_status"])


def downgrade() -> None:
    op.drop_index("ix_event_matches_status", table_name="event_matches")
    op.drop_index("ix_mv_intervention_mix_country_month", table_name="mv_intervention_mix")
    op.drop_index("ix_mv_workflow_governance_country_month", table_name="mv_workflow_governance")
    op.drop_index("ix_mv_unmatched_events_country_month", table_name="mv_unmatched_events")
    op.drop_index("ix_mv_execution_kpis_country_month", table_name="mv_execution_kpis")
    for view_name in ["mv_intervention_mix", "mv_workflow_governance", "mv_unmatched_events", "mv_execution_kpis"]:
        op.execute(f"drop materialized view if exists {view_name}")
    op.execute("drop view if exists phase4_analysis_scope")


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(encoding="utf-8")
