"""phase 5-7 architecture corrections

Revision ID: 0019_phase5_7_fix
Revises: 0018_data_quality_view
Create Date: 2026-06-19
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0019_phase5_7_fix"
down_revision: str | None = "0018_data_quality_view"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("drop materialized view if exists mv_data_quality")
    op.execute("drop materialized view if exists mv_doctor_roi")
    op.execute("drop materialized view if exists mv_budget_utilization")

    op.execute(_read_view_sql("mv_budget_utilization.sql"))
    op.create_index("ix_mv_budget_utilization_country_month", "mv_budget_utilization", ["country_id", "calendar_month_id"])
    op.create_index("ix_mv_budget_utilization_scope", "mv_budget_utilization", ["is_primary_phase4_scope"])
    op.create_index("ix_mv_budget_utilization_match_status", "mv_budget_utilization", ["match_status"])

    op.execute(_read_view_sql("mv_doctor_roi.sql"))
    op.create_index("ix_mv_doctor_roi_country_pcode", "mv_doctor_roi", ["country_id", "pcode_normalized"])
    op.create_index("ix_mv_doctor_roi_segment", "mv_doctor_roi", ["roi_segment"])
    op.create_index("ix_mv_doctor_roi_quadrant", "mv_doctor_roi", ["quadrant_label"])
    op.create_index("ix_mv_doctor_roi_engagement_window", "mv_doctor_roi", ["first_engagement_date", "last_engagement_date"])

    op.execute(_read_view_sql("mv_data_quality.sql"))
    op.create_index("ix_mv_data_quality_latest_run", "mv_data_quality", ["latest_ingestion_run_id"])

    op.execute("refresh materialized view mv_budget_utilization")
    op.execute("refresh materialized view mv_doctor_roi")
    op.execute("refresh materialized view mv_data_quality")


def downgrade() -> None:
    op.execute("drop materialized view if exists mv_data_quality")
    op.execute("drop materialized view if exists mv_doctor_roi")
    op.execute("drop materialized view if exists mv_budget_utilization")


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(encoding="utf-8")
