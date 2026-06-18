"""phase 4 real data repair views

Revision ID: 0012_phase4_data_repairs
Revises: 0011_phase4_matrix_fixes
Create Date: 2026-06-18
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0012_phase4_data_repairs"
down_revision: str | None = "0011_phase4_matrix_fixes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("drop index if exists ix_mv_execution_kpis_country_month")
    op.execute("drop index if exists ix_mv_workflow_governance_country_month")
    op.execute("drop materialized view if exists mv_execution_kpis")
    op.execute("drop materialized view if exists mv_workflow_governance")

    op.execute(_read_view_sql("mv_execution_kpis.sql"))
    op.execute(_read_view_sql("mv_workflow_governance.sql"))

    op.create_index("ix_mv_execution_kpis_country_month", "mv_execution_kpis", ["country_id", "calendar_month_id"])
    op.create_index("ix_mv_workflow_governance_country_month", "mv_workflow_governance", ["country_id", "calendar_month_id"])
    op.execute(_read_view_sql("refresh_materialized_views.sql"))


def downgrade() -> None:
    op.execute("drop index if exists ix_mv_execution_kpis_country_month")
    op.execute("drop index if exists ix_mv_workflow_governance_country_month")
    op.execute("drop materialized view if exists mv_execution_kpis")
    op.execute("drop materialized view if exists mv_workflow_governance")


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(encoding="utf-8")
