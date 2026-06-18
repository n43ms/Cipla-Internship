"""phase 4 semantic repairs

Revision ID: 0014_phase4_semantic_repairs
Revises: 0013_phase4_scope_quality
Create Date: 2026-06-18
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0014_phase4_semantic_repairs"
down_revision: str | None = "0013_phase4_scope_quality"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


MATERIALIZED_VIEWS = [
    "mv_intervention_mix",
    "mv_workflow_governance",
    "mv_execution_event_matrix",
    "mv_unmatched_events",
    "mv_execution_kpis",
]


def upgrade() -> None:
    _drop_phase4_views()
    _backfill_snapshot_reasons()
    for view_file in [
        "mv_execution_kpis.sql",
        "mv_unmatched_events.sql",
        "mv_execution_event_matrix.sql",
        "mv_workflow_governance.sql",
        "mv_intervention_mix.sql",
    ]:
        op.execute(_read_view_sql(view_file))
    _create_indexes()
    op.execute(_read_view_sql("refresh_materialized_views.sql"))
    op.execute("select refresh_dashboard_materialized_views()")


def downgrade() -> None:
    _drop_phase4_views()
    for view_file in [
        "mv_execution_kpis.sql",
        "mv_unmatched_events.sql",
        "mv_execution_event_matrix.sql",
        "mv_workflow_governance.sql",
        "mv_intervention_mix.sql",
    ]:
        op.execute(_read_view_sql(view_file))
    _create_indexes()
    op.execute(_read_view_sql("refresh_materialized_views.sql"))
    op.execute("select refresh_dashboard_materialized_views()")


def _drop_phase4_views() -> None:
    for index_name in [
        "ix_mv_execution_kpis_country_month",
        "ix_mv_execution_kpis_scope",
        "ix_mv_unmatched_events_country_month",
        "ix_mv_execution_event_matrix_country_month",
        "ix_mv_execution_event_matrix_status",
        "ix_mv_intervention_mix_country_month",
        "ix_mv_intervention_mix_scope",
        "ix_mv_workflow_governance_country_month",
        "ix_mv_workflow_governance_scope",
    ]:
        op.execute(f"drop index if exists {index_name}")
    for view_name in MATERIALIZED_VIEWS:
        op.execute(f"drop materialized view if exists {view_name}")


def _create_indexes() -> None:
    op.create_index("ix_mv_execution_kpis_country_month", "mv_execution_kpis", ["country_id", "calendar_month_id"])
    op.create_index("ix_mv_execution_kpis_scope", "mv_execution_kpis", ["is_primary_phase4_scope"])
    op.create_index("ix_mv_unmatched_events_country_month", "mv_unmatched_events", ["country_id", "calendar_month_id"])
    op.create_index(
        "ix_mv_execution_event_matrix_country_month",
        "mv_execution_event_matrix",
        ["country_id", "calendar_month_id"],
    )
    op.create_index("ix_mv_execution_event_matrix_status", "mv_execution_event_matrix", ["match_status"])
    op.create_index("ix_mv_intervention_mix_country_month", "mv_intervention_mix", ["country_id", "calendar_month_id"])
    op.create_index("ix_mv_intervention_mix_scope", "mv_intervention_mix", ["is_primary_phase4_scope"])
    op.create_index(
        "ix_mv_workflow_governance_country_month",
        "mv_workflow_governance",
        ["country_id", "calendar_month_id"],
    )
    op.create_index("ix_mv_workflow_governance_scope", "mv_workflow_governance", ["is_primary_phase4_scope"])


def _backfill_snapshot_reasons() -> None:
    op.execute(
        """
        update event_matches em
        set unmatched_reason_code = 'snapshot_only_no_matching_plan',
            unmatched_reason_detail = 'The snapshot row has no matching planner event in the same scoped country/month.'
        from phase4_analysis_scope p4
        where p4.country_id = em.country_id
          and p4.calendar_month_id = em.calendar_month_id
          and em.match_status = 'unmatched_snapshot'
          and p4.in_primary_scope
        """
    )


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(encoding="utf-8")
