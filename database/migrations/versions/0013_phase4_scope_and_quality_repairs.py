"""phase 4 scope and quality repairs

Revision ID: 0013_phase4_scope_quality
Revises: 0012_phase4_data_repairs
Create Date: 2026-06-18
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0013_phase4_scope_quality"
down_revision: str | None = "0012_phase4_data_repairs"
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
    op.execute("alter table event_matches add column if not exists unmatched_reason_code text")
    op.execute("alter table event_matches add column if not exists unmatched_reason_detail text")
    op.execute(_read_view_sql("phase4_analysis_scope.sql"))
    op.execute(_read_view_sql("mv_latest_file_ingestion_status.sql"))
    op.execute(_read_view_sql("mv_latest_validation_errors.sql"))
    _backfill_source_file_periods()
    _backfill_unmatched_reasons()
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


def downgrade() -> None:
    _drop_phase4_views()
    op.execute("drop view if exists mv_latest_validation_errors")
    op.execute("drop view if exists mv_latest_file_ingestion_status")
    op.execute("drop view if exists phase4_analysis_scope")
    op.execute("alter table event_matches drop column if exists unmatched_reason_detail")
    op.execute("alter table event_matches drop column if exists unmatched_reason_code")


def _drop_phase4_views() -> None:
    for index_name in [
        "ix_mv_execution_kpis_country_month",
        "ix_mv_unmatched_events_country_month",
        "ix_mv_execution_event_matrix_country_month",
        "ix_mv_execution_event_matrix_status",
        "ix_mv_intervention_mix_country_month",
        "ix_mv_intervention_mix_scope",
        "ix_mv_execution_kpis_scope",
        "ix_mv_workflow_governance_country_month",
        "ix_event_matches_unmatched_reason",
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
    op.create_index("ix_event_matches_unmatched_reason", "event_matches", ["unmatched_reason_code"])


def _backfill_source_file_periods() -> None:
    op.execute(
        """
        with file_periods as (
            select source_file_id, min(month_start_date) period_start, max(month_start_date) period_end
            from (
                select pe.source_file_id, cm.month_start_date
                from plan_events pe
                join calendar_months cm on cm.id = pe.calendar_month_id
                union all
                select es.source_file_id, cm.month_start_date
                from execution_snapshots es
                join calendar_months cm on cm.id = es.calendar_month_id
                union all
                select er.source_file_id, cm.month_start_date
                from execution_requests er
                join calendar_months cm on cm.id = er.calendar_month_id
                union all
                select rdm.source_file_id, cm.month_start_date
                from rcpa_doctor_month_summary rdm
                join calendar_months cm on cm.id = rdm.calendar_month_id
                union all
                select rcb.source_file_id, cm.month_start_date
                from rcpa_country_brand_month_summary rcb
                join calendar_months cm on cm.id = rcb.calendar_month_id
                union all
                select rdb.source_file_id, cm_first.month_start_date
                from rcpa_doctor_brand_summary rdb
                join calendar_months cm_first on cm_first.id = rdb.first_calendar_month_id
                union all
                select rdb.source_file_id, cm_last.month_start_date
                from rcpa_doctor_brand_summary rdb
                join calendar_months cm_last on cm_last.id = rdb.last_calendar_month_id
            ) periods
            group by source_file_id
        )
        update source_files sf
        set period_start = fp.period_start,
            period_end = fp.period_end
        from file_periods fp
        where fp.source_file_id = sf.id
        """
    )


def _backfill_unmatched_reasons() -> None:
    op.execute(
        """
        update event_matches em
        set
            unmatched_reason_code = case
                when em.match_status = 'weak_match' then 'name_mismatch'
                when p4.country_name not in ('Nepal', 'Sri Lanka') then 'no_planner_for_country'
                when p4.month_label < '2026-04' then 'historical_request_no_fy27_plan'
                when p4.month_label > '2026-05' then 'future_plan_no_execution_yet'
                when not p4.planner_available then 'no_planner_for_country'
                when em.match_status = 'unmatched_plan' and not p4.snapshot_available then 'no_snapshot_for_month'
                when em.match_status = 'unmatched_plan' then 'planner_only'
                when em.match_status = 'unmatched_snapshot' then 'snapshot_only_no_matching_plan'
                when em.match_status = 'unmatched_request' then 'consolidation_only'
                else null
            end,
            unmatched_reason_detail = case
                when em.match_status = 'weak_match' then 'The event name matched only weakly and must be reviewed before treating it as final execution evidence.'
                when p4.country_name not in ('Nepal', 'Sri Lanka') then 'This market has no FY27 planner in the supplied Phase 4 source set.'
                when p4.month_label < '2026-04' then 'This request is before FY27 planner coverage and is retained as historical consolidation evidence.'
                when p4.month_label > '2026-05' then 'This record is outside the April-May 2026 execution snapshot window and is retained for future analysis.'
                when not p4.planner_available then 'No planner row exists for this country/month.'
                when em.match_status = 'unmatched_plan' and not p4.snapshot_available then 'No execution snapshot exists for this planned event month.'
                when em.match_status = 'unmatched_plan' then 'The planned event has no confident matching execution or consolidation evidence.'
                when em.match_status = 'unmatched_snapshot' then 'The snapshot row has no matching planner event in the same scoped country/month.'
                when em.match_status = 'unmatched_request' then 'The consolidation request has no matching planner event.'
                else null
            end
        from phase4_analysis_scope p4
        where p4.country_id = em.country_id
          and p4.calendar_month_id = em.calendar_month_id
          and em.match_status in ('weak_match', 'unmatched_plan', 'unmatched_snapshot', 'unmatched_request')
        """
    )


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(encoding="utf-8")
