"""execution snapshot derivation provenance

Revision ID: 0015_snapshot_provenance
Revises: 0014_phase4_semantic_repairs
Create Date: 2026-06-18
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0015_snapshot_provenance"
down_revision: str | None = "0014_phase4_semantic_repairs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        alter table execution_snapshots
        add column if not exists source_derivation_json json not null default '{}'::json
        """
    )
    op.execute(
        """
        update execution_snapshots es
        set source_derivation_json = jsonb_build_object(
            'method', 'grouped_from_consolidation',
            'reason', 'Sri Lanka May monthly execution tab is missing; derived from consolidation requests.',
            'source_sheet_name', es.source_sheet_name,
            'contributing_request_count', coalesce(src.request_count, 0),
            'contributing_request_ids', coalesce(src.request_ids, '[]'::jsonb),
            'contributing_source_rows', coalesce(src.source_rows, '[]'::jsonb)
        )::json
        from (
            select
                er.country_id,
                er.calendar_month_id,
                er.intervention_name_normalized,
                er.intervention_type,
                count(*) as request_count,
                jsonb_agg(er.req_id order by er.source_row_number) filter (where er.req_id is not null) as request_ids,
                jsonb_agg(er.source_row_number order by er.source_row_number) as source_rows
            from execution_requests er
            join countries c on c.id = er.country_id
            join calendar_months cm on cm.id = er.calendar_month_id
            where c.name = 'Sri Lanka'
              and cm.month_label = '2026-05'
            group by er.country_id, er.calendar_month_id, er.intervention_name_normalized, er.intervention_type
        ) src
        where es.country_id = src.country_id
          and es.calendar_month_id = src.calendar_month_id
          and es.event_name_normalized = src.intervention_name_normalized
          and coalesce(es.event_type, '') = coalesce(src.intervention_type, '')
          and es.snapshot_source = 'derived_from_consolidation'
        """
    )
    _recreate_event_matrix()


def downgrade() -> None:
    _drop_event_matrix()
    op.drop_column("execution_snapshots", "source_derivation_json")
    op.execute(_read_view_sql("mv_execution_event_matrix.sql"))
    op.create_index(
        "ix_mv_execution_event_matrix_country_month",
        "mv_execution_event_matrix",
        ["country_id", "calendar_month_id"],
    )
    op.create_index("ix_mv_execution_event_matrix_status", "mv_execution_event_matrix", ["match_status"])


def _recreate_event_matrix() -> None:
    _drop_event_matrix()
    op.execute(_read_view_sql("mv_execution_event_matrix.sql"))
    op.create_index(
        "ix_mv_execution_event_matrix_country_month",
        "mv_execution_event_matrix",
        ["country_id", "calendar_month_id"],
    )
    op.create_index("ix_mv_execution_event_matrix_status", "mv_execution_event_matrix", ["match_status"])
    op.execute("refresh materialized view mv_execution_event_matrix")


def _drop_event_matrix() -> None:
    op.execute("drop index if exists ix_mv_execution_event_matrix_country_month")
    op.execute("drop index if exists ix_mv_execution_event_matrix_status")
    op.execute("drop materialized view if exists mv_execution_event_matrix")


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(encoding="utf-8")
