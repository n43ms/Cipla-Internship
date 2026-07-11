"""add sponsorship outcome view

Revision ID: 0025_sponsorship_outcomes
Revises: 0024_rcpa_provenance
Create Date: 2026-07-11
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0025_sponsorship_outcomes"
down_revision: str | None = "0024_rcpa_provenance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("drop materialized view if exists mv_sponsorship_outcomes")
    op.execute(_read_view_sql("mv_sponsorship_outcomes.sql"))
    op.create_index(
        "ix_mv_sponsorship_outcomes_country_pcode",
        "mv_sponsorship_outcomes",
        ["country_id", "pcode_normalized"],
    )
    op.create_index(
        "ix_mv_sponsorship_outcomes_confidence",
        "mv_sponsorship_outcomes",
        ["evidence_confidence"],
    )
    op.execute(_read_view_sql("refresh_materialized_views.sql"))
    op.execute("refresh materialized view mv_sponsorship_outcomes")


def downgrade() -> None:
    op.execute("drop materialized view if exists mv_sponsorship_outcomes")


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(encoding="utf-8")
