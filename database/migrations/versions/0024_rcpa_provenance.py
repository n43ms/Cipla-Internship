"""add RCPA mapping provenance metadata

Revision ID: 0024_rcpa_provenance
Revises: 0023_doctor_engagement_facts
Create Date: 2026-07-11
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op
import sqlalchemy as sa

revision: str = "0024_rcpa_provenance"
down_revision: str | None = "0023_doctor_engagement_facts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("rcpa_doctor_month_summary", sa.Column("territory_name", sa.Text()))
    op.add_column(
        "rcpa_doctor_month_summary",
        sa.Column("mapping_provenance", sa.Text(), nullable=False, server_default="unknown"),
    )
    op.add_column("rcpa_doctor_month_summary", sa.Column("mapping_note", sa.Text()))
    op.add_column("rcpa_doctor_month_summary", sa.Column("source_mapping_method", sa.Text()))
    op.add_column("rcpa_doctor_month_summary", sa.Column("competitor_filter_note", sa.Text()))
    op.create_index(
        "ix_rcpa_doctor_month_summary_mapping_provenance",
        "rcpa_doctor_month_summary",
        ["mapping_provenance"],
    )
    op.execute("drop materialized view if exists mv_data_quality")
    op.execute(_read_view_sql("mv_data_quality.sql"))
    op.create_index("ix_mv_data_quality_latest_run", "mv_data_quality", ["latest_ingestion_run_id"])
    op.execute("refresh materialized view mv_data_quality")


def downgrade() -> None:
    op.execute("drop materialized view if exists mv_data_quality")
    op.drop_index(
        "ix_rcpa_doctor_month_summary_mapping_provenance",
        table_name="rcpa_doctor_month_summary",
    )
    op.drop_column("rcpa_doctor_month_summary", "competitor_filter_note")
    op.drop_column("rcpa_doctor_month_summary", "source_mapping_method")
    op.drop_column("rcpa_doctor_month_summary", "mapping_note")
    op.drop_column("rcpa_doctor_month_summary", "mapping_provenance")
    op.drop_column("rcpa_doctor_month_summary", "territory_name")


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(encoding="utf-8")
