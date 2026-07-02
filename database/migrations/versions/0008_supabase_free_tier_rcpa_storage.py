"""supabase free-tier RCPA storage

Revision ID: 0008_rcpa_free_storage
Revises: 0007_phase_1_3_schema_completion
Create Date: 2026-06-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008_rcpa_free_storage"
down_revision: str | None = "0007_phase_1_3_schema_completion"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def uuid_pk() -> sa.Column:
    return sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()"))


def source_cols() -> list[sa.Column]:
    return [
        sa.Column("source_file_id", sa.UUID(), sa.ForeignKey("source_files.id"), nullable=False),
        sa.Column("ingestion_run_id", sa.UUID(), sa.ForeignKey("ingestion_runs.id"), nullable=False),
    ]


def upgrade() -> None:
    # Supabase Free is 500 MB. The old SKU/source-grain RCPA table alone reached ~587 MB.
    # The detailed evidence is retained in gitignored local extracts under data/processed/.
    op.execute("TRUNCATE TABLE rcpa_prescriptions")

    op.create_table(
        "rcpa_doctor_month_summary",
        uuid_pk(),
        *source_cols(),
        sa.Column("country_id", sa.UUID(), sa.ForeignKey("countries.id"), nullable=False),
        sa.Column("calendar_month_id", sa.UUID(), sa.ForeignKey("calendar_months.id"), nullable=False),
        sa.Column("pcode_raw", sa.Text()),
        sa.Column("pcode_normalized", sa.Text(), nullable=False),
        sa.Column("doctor_name", sa.Text()),
        sa.Column("speciality", sa.Text()),
        sa.Column("doctor_class", sa.Text()),
        sa.Column("patch_name", sa.Text()),
        sa.Column("active_status", sa.Text()),
        sa.Column("own_prescription_qty", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("own_prescription_value_local", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("competitor_prescription_qty", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("competitor_prescription_value_local", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("total_prescription_qty", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("total_prescription_value_local", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("currency_code", sa.Text(), nullable=False),
        sa.Column("row_count_aggregated", sa.Integer(), nullable=False),
        sa.UniqueConstraint(
            "source_file_id",
            "country_id",
            "calendar_month_id",
            "pcode_normalized",
            "currency_code",
            name="uq_rcpa_doctor_month_summary_grain",
        ),
    )
    op.create_table(
        "rcpa_doctor_brand_summary",
        uuid_pk(),
        *source_cols(),
        sa.Column("country_id", sa.UUID(), sa.ForeignKey("countries.id"), nullable=False),
        sa.Column("first_calendar_month_id", sa.UUID(), sa.ForeignKey("calendar_months.id")),
        sa.Column("last_calendar_month_id", sa.UUID(), sa.ForeignKey("calendar_months.id")),
        sa.Column("pcode_normalized", sa.Text(), nullable=False),
        sa.Column("doctor_name", sa.Text()),
        sa.Column("brand_group", sa.Text(), nullable=False),
        sa.Column("own_or_competitor", sa.Text(), nullable=False),
        sa.Column("prescription_qty", sa.Numeric(18, 2), nullable=False),
        sa.Column("prescription_value_local", sa.Numeric(18, 2)),
        sa.Column("currency_code", sa.Text(), nullable=False),
        sa.Column("row_count_aggregated", sa.Integer(), nullable=False),
        sa.UniqueConstraint(
            "source_file_id",
            "country_id",
            "pcode_normalized",
            "brand_group",
            "own_or_competitor",
            "currency_code",
            name="uq_rcpa_doctor_brand_summary_grain",
        ),
    )
    op.create_table(
        "rcpa_country_brand_month_summary",
        uuid_pk(),
        *source_cols(),
        sa.Column("country_id", sa.UUID(), sa.ForeignKey("countries.id"), nullable=False),
        sa.Column("calendar_month_id", sa.UUID(), sa.ForeignKey("calendar_months.id"), nullable=False),
        sa.Column("brand_group", sa.Text(), nullable=False),
        sa.Column("own_or_competitor", sa.Text(), nullable=False),
        sa.Column("prescription_qty", sa.Numeric(18, 2), nullable=False),
        sa.Column("prescription_value_local", sa.Numeric(18, 2)),
        sa.Column("currency_code", sa.Text(), nullable=False),
        sa.Column("row_count_aggregated", sa.Integer(), nullable=False),
        sa.UniqueConstraint(
            "source_file_id",
            "country_id",
            "calendar_month_id",
            "brand_group",
            "own_or_competitor",
            "currency_code",
            name="uq_rcpa_country_brand_month_summary_grain",
        ),
    )
    op.create_index(
        "ix_rcpa_doctor_month_summary_country_month",
        "rcpa_doctor_month_summary",
        ["country_id", "calendar_month_id"],
    )
    op.create_index(
        "ix_rcpa_doctor_month_summary_pcode",
        "rcpa_doctor_month_summary",
        ["country_id", "pcode_normalized"],
    )
    op.create_index(
        "ix_rcpa_doctor_brand_summary_pcode",
        "rcpa_doctor_brand_summary",
        ["country_id", "pcode_normalized"],
    )
    op.create_index(
        "ix_rcpa_country_brand_month_summary_country_month",
        "rcpa_country_brand_month_summary",
        ["country_id", "calendar_month_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_rcpa_country_brand_month_summary_country_month",
        table_name="rcpa_country_brand_month_summary",
    )
    op.drop_index("ix_rcpa_doctor_brand_summary_pcode", table_name="rcpa_doctor_brand_summary")
    op.drop_index("ix_rcpa_doctor_month_summary_pcode", table_name="rcpa_doctor_month_summary")
    op.drop_index(
        "ix_rcpa_doctor_month_summary_country_month",
        table_name="rcpa_doctor_month_summary",
    )
    op.drop_table("rcpa_country_brand_month_summary")
    op.drop_table("rcpa_doctor_brand_summary")
    op.drop_table("rcpa_doctor_month_summary")
