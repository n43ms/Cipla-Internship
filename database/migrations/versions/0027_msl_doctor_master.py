"""MSL doctor master enrichment

Revision ID: 0027_msl_doctor_master
Revises: 0026_territory_opportunity
Create Date: 2026-07-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0027_msl_doctor_master"
down_revision: str | None = "0026_territory_opportunity"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "doctor_master_mappings",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("source_file_id", sa.UUID(), sa.ForeignKey("source_files.id"), nullable=False),
        sa.Column(
            "ingestion_run_id",
            sa.UUID(),
            sa.ForeignKey("ingestion_runs.id"),
            nullable=False,
        ),
        sa.Column("country_id", sa.UUID(), sa.ForeignKey("countries.id"), nullable=False),
        sa.Column("pcode_raw", sa.Text()),
        sa.Column("pcode_normalized", sa.Text(), nullable=False),
        sa.Column("doctor_name", sa.Text(), nullable=False),
        sa.Column("doctor_short_name", sa.Text()),
        sa.Column("doctor_name_normalized", sa.Text(), nullable=False),
        sa.Column("territory_name", sa.Text()),
        sa.Column("territory_id", sa.Text()),
        sa.Column("patch", sa.Text()),
        sa.Column("patch_name", sa.Text()),
        sa.Column("legacy_code", sa.Text()),
        sa.Column("speciality", sa.Text()),
        sa.Column("doctor_class", sa.Text()),
        sa.Column("taskforce", sa.Text()),
        sa.Column("rep_name", sa.Text()),
        sa.Column("rep_code", sa.Text()),
        sa.Column("employee_id", sa.Text()),
        sa.Column("manager_name", sa.Text()),
        sa.Column("town", sa.Text()),
        sa.Column("cis_no", sa.Text()),
        sa.Column("registration_no", sa.Text()),
        sa.Column("gender", sa.Text()),
        sa.Column("source_sheet_name", sa.Text(), nullable=False),
        sa.Column("source_row_number", sa.Integer(), nullable=False),
        sa.Column("source_row_hash", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "source_file_id",
            "source_row_hash",
            name="uq_doctor_master_mappings_source_row_hash",
        ),
    )
    op.create_index(
        "ix_doctor_master_country_pcode",
        "doctor_master_mappings",
        ["country_id", "pcode_normalized"],
    )
    op.create_index(
        "ix_doctor_master_country_name",
        "doctor_master_mappings",
        ["country_id", "doctor_name_normalized"],
    )
    op.create_index(
        "ix_doctor_master_country_territory",
        "doctor_master_mappings",
        ["country_id", "territory_name"],
    )

    op.add_column("doctors", sa.Column("doctor_name_normalized", sa.Text()))
    op.add_column("doctors", sa.Column("territory_name", sa.Text()))
    op.add_column("doctors", sa.Column("territory_id", sa.Text()))
    op.add_column("doctors", sa.Column("legacy_code", sa.Text()))
    op.add_column(
        "doctors",
        sa.Column("doctor_master_source_file_id", sa.UUID(), sa.ForeignKey("source_files.id")),
    )
    op.create_index("ix_doctors_country_name", "doctors", ["country_id", "doctor_name_normalized"])
    op.create_index("ix_doctors_country_territory", "doctors", ["country_id", "territory_name"])


def downgrade() -> None:
    op.drop_index("ix_doctors_country_territory", table_name="doctors")
    op.drop_index("ix_doctors_country_name", table_name="doctors")
    op.drop_column("doctors", "doctor_master_source_file_id")
    op.drop_column("doctors", "legacy_code")
    op.drop_column("doctors", "territory_id")
    op.drop_column("doctors", "territory_name")
    op.drop_column("doctors", "doctor_name_normalized")

    op.drop_index("ix_doctor_master_country_territory", table_name="doctor_master_mappings")
    op.drop_index("ix_doctor_master_country_name", table_name="doctor_master_mappings")
    op.drop_index("ix_doctor_master_country_pcode", table_name="doctor_master_mappings")
    op.drop_table("doctor_master_mappings")
