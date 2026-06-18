"""doctor roi quadrant view

Revision ID: 0017_doctor_roi_quadrant_view
Revises: 0016_budget_finance_view
Create Date: 2026-06-19
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0017_doctor_roi_quadrant_view"
down_revision: str | None = "0016_budget_finance_view"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("drop materialized view if exists mv_doctor_roi")
    op.execute(_read_view_sql("mv_doctor_roi.sql"))
    op.create_index("ix_mv_doctor_roi_country_pcode", "mv_doctor_roi", ["country_id", "pcode_normalized"])
    op.create_index("ix_mv_doctor_roi_segment", "mv_doctor_roi", ["roi_segment"])
    op.create_index("ix_mv_doctor_roi_quadrant", "mv_doctor_roi", ["quadrant_label"])
    op.create_index("ix_request_doctors_pcode_attendance", "request_doctors", ["pcode_normalized", "attendance_type"])
    op.create_index("ix_rcpa_doctor_month_country_pcode", "rcpa_doctor_month_summary", ["country_id", "pcode_normalized"])
    op.execute("refresh materialized view mv_doctor_roi")


def downgrade() -> None:
    op.drop_index("ix_rcpa_doctor_month_country_pcode", table_name="rcpa_doctor_month_summary")
    op.drop_index("ix_request_doctors_pcode_attendance", table_name="request_doctors")
    op.drop_index("ix_mv_doctor_roi_quadrant", table_name="mv_doctor_roi")
    op.drop_index("ix_mv_doctor_roi_segment", table_name="mv_doctor_roi")
    op.drop_index("ix_mv_doctor_roi_country_pcode", table_name="mv_doctor_roi")
    op.execute("drop materialized view if exists mv_doctor_roi")


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(encoding="utf-8")
