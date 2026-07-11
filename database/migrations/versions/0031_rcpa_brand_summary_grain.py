"""restore slim RCPA brand summary grain constraint

Revision ID: 0031_brand_grain
Revises: 0030_storage_slim
Create Date: 2026-07-11
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0031_brand_grain"
down_revision: str | None = "0030_storage_slim"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_rcpa_doctor_brand_summary_grain",
        "rcpa_doctor_brand_summary",
        [
            "source_file_id",
            "country_id",
            "pcode_normalized",
            "brand_group",
            "own_or_competitor",
            "currency_code",
        ],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_rcpa_doctor_brand_summary_grain",
        "rcpa_doctor_brand_summary",
        type_="unique",
    )
