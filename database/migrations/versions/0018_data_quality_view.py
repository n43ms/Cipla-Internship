"""data quality view

Revision ID: 0018_data_quality_view
Revises: 0017_doctor_roi_quadrant_view
Create Date: 2026-06-19
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0018_data_quality_view"
down_revision: str | None = "0017_doctor_roi_quadrant_view"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("drop materialized view if exists mv_data_quality")
    op.execute(_read_view_sql("mv_data_quality.sql"))
    op.create_index("ix_mv_data_quality_latest_run", "mv_data_quality", ["latest_ingestion_run_id"])
    op.create_index("ix_validation_errors_latest_lookup", "validation_errors", ["source_file_id", "severity"])
    op.execute("refresh materialized view mv_data_quality")


def downgrade() -> None:
    op.drop_index("ix_validation_errors_latest_lookup", table_name="validation_errors")
    op.drop_index("ix_mv_data_quality_latest_run", table_name="mv_data_quality")
    op.execute("drop materialized view if exists mv_data_quality")


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(encoding="utf-8")
