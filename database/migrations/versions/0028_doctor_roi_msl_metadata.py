"""expose MSL doctor metadata in Doctor ROI

Revision ID: 0028_doctor_roi_msl_metadata
Revises: 0027_msl_doctor_master
Create Date: 2026-07-11
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0028_doctor_roi_msl_metadata"
down_revision: str | None = "0027_msl_doctor_master"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("drop materialized view if exists mv_data_quality")
    op.execute("drop materialized view if exists mv_doctor_roi")
    op.execute(_read_view_sql("mv_doctor_roi.sql"))
    _create_doctor_roi_indexes()
    op.execute(_read_view_sql("mv_data_quality.sql"))
    op.create_index("ix_mv_data_quality_latest_run", "mv_data_quality", ["latest_ingestion_run_id"])
    op.execute("refresh materialized view mv_doctor_roi")
    op.execute("refresh materialized view mv_data_quality")


def downgrade() -> None:
    op.execute("drop materialized view if exists mv_data_quality")
    op.execute("drop materialized view if exists mv_doctor_roi")
    op.execute(_read_view_sql("mv_doctor_roi.sql"))
    _create_doctor_roi_indexes()
    op.execute(_read_view_sql("mv_data_quality.sql"))
    op.create_index("ix_mv_data_quality_latest_run", "mv_data_quality", ["latest_ingestion_run_id"])
    op.execute("refresh materialized view mv_doctor_roi")
    op.execute("refresh materialized view mv_data_quality")


def _create_doctor_roi_indexes() -> None:
    op.create_index(
        "ix_mv_doctor_roi_country_pcode",
        "mv_doctor_roi",
        ["country_id", "pcode_normalized"],
    )
    op.create_index("ix_mv_doctor_roi_segment", "mv_doctor_roi", ["roi_segment"])
    op.create_index("ix_mv_doctor_roi_quadrant", "mv_doctor_roi", ["quadrant_label"])
    op.create_index(
        "ix_mv_doctor_roi_engagement_window",
        "mv_doctor_roi",
        ["first_engagement_date", "last_engagement_date"],
    )
    op.create_index(
        "ix_mv_doctor_roi_territory",
        "mv_doctor_roi",
        ["country_id", "territory_name"],
    )


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(
        encoding="utf-8"
    )
