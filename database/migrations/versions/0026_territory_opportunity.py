"""territory opportunity materialized view

Revision ID: 0026_territory_opportunity
Revises: 0025_sponsorship_outcomes
Create Date: 2026-07-11
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0026_territory_opportunity"
down_revision: str | None = "0025_sponsorship_outcomes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("drop materialized view if exists mv_territory_opportunity")
    op.execute(_read_view_sql("mv_territory_opportunity.sql"))
    op.create_index(
        "ix_mv_territory_opportunity_country_label",
        "mv_territory_opportunity",
        ["country_id", "opportunity_label"],
    )
    op.create_index(
        "ix_mv_territory_opportunity_country_territory",
        "mv_territory_opportunity",
        ["country_id", "territory_name"],
    )
    op.execute(_read_view_sql("refresh_materialized_views.sql"))
    op.execute("refresh materialized view mv_territory_opportunity")


def downgrade() -> None:
    op.drop_index(
        "ix_mv_territory_opportunity_country_territory",
        table_name="mv_territory_opportunity",
    )
    op.drop_index(
        "ix_mv_territory_opportunity_country_label",
        table_name="mv_territory_opportunity",
    )
    op.execute("drop materialized view if exists mv_territory_opportunity")


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(encoding="utf-8")
