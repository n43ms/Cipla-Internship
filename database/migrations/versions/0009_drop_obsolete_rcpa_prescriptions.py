"""drop obsolete RCPA prescription table

Revision ID: 0009_drop_rcpa_prescriptions
Revises: 0008_rcpa_free_storage
Create Date: 2026-06-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009_drop_rcpa_prescriptions"
down_revision: str | None = "0008_rcpa_free_storage"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def uuid_pk() -> sa.Column:
    return sa.Column(
        "id",
        sa.UUID(),
        primary_key=True,
        server_default=sa.text("uuid_generate_v4()"),
    )


def source_cols() -> list[sa.Column]:
    return [
        sa.Column("source_file_id", sa.UUID(), sa.ForeignKey("source_files.id"), nullable=False),
        sa.Column("ingestion_run_id", sa.UUID(), sa.ForeignKey("ingestion_runs.id"), nullable=False),
    ]


def upgrade() -> None:
    op.drop_table("rcpa_prescriptions")


def downgrade() -> None:
    op.create_table(
        "rcpa_prescriptions",
        uuid_pk(),
        *source_cols(),
        sa.Column("country_id", sa.UUID(), sa.ForeignKey("countries.id"), nullable=False),
        sa.Column(
            "calendar_month_id",
            sa.UUID(),
            sa.ForeignKey("calendar_months.id"),
            nullable=False,
        ),
        sa.Column("pcode_raw", sa.Text()),
        sa.Column("pcode_normalized", sa.Text(), nullable=False),
        sa.Column("doctor_name", sa.Text()),
        sa.Column("brand_group", sa.Text(), nullable=False),
        sa.Column("sku", sa.Text(), nullable=False),
        sa.Column("own_or_competitor", sa.Text(), nullable=False),
        sa.Column("prescription_qty", sa.Numeric(18, 2), nullable=False),
        sa.Column("prescription_value_local", sa.Numeric(18, 2)),
        sa.Column("currency_code", sa.Text(), nullable=False),
        sa.Column("prescription_value_usd", sa.Numeric(18, 2)),
        sa.Column("row_count_aggregated", sa.Integer(), nullable=False),
        sa.Column("speciality", sa.Text()),
        sa.Column("doctor_class", sa.Text()),
        sa.Column("patch_name", sa.Text()),
        sa.Column("active_status", sa.Text()),
        sa.Column("sku_detail", sa.Text()),
    )
    op.create_index(
        "ix_rcpa_prescriptions_country_month",
        "rcpa_prescriptions",
        ["country_id", "calendar_month_id"],
    )
    op.create_unique_constraint(
        "uq_rcpa_aggregate_grain",
        "rcpa_prescriptions",
        [
            "source_file_id",
            "country_id",
            "calendar_month_id",
            "pcode_normalized",
            "brand_group",
            "sku",
            "own_or_competitor",
            "currency_code",
        ],
    )
