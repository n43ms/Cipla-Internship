"""remove self-serving territory label

Revision ID: 0029_territory_labels
Revises: 0028_doctor_roi_msl_metadata
Create Date: 2026-07-11
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0029_territory_labels"
down_revision: str | None = "0028_doctor_roi_msl_metadata"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("drop materialized view if exists mv_territory_opportunity")
    op.execute(_read_view_sql("mv_territory_opportunity.sql"))
    _create_indexes()
    op.execute("refresh materialized view mv_territory_opportunity")


def downgrade() -> None:
    op.execute("drop materialized view if exists mv_territory_opportunity")
    op.execute(_read_view_sql("mv_territory_opportunity.sql"))
    _create_indexes()
    op.execute("refresh materialized view mv_territory_opportunity")


def _create_indexes() -> None:
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


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(
        encoding="utf-8"
    )
