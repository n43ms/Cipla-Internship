"""slim retained serving tables for Supabase storage

Revision ID: 0030_storage_slim
Revises: 0029_territory_labels
Create Date: 2026-07-11
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0030_storage_slim"
down_revision: str | None = "0029_territory_labels"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # MSL rows are staging-only after they enrich doctors and doctor_engagement_facts.
    op.drop_table("doctor_master_mappings")

    # Keep the unique doctor-month grain and lookup indexes, but remove duplicate/non-serving indexes.
    op.execute("drop index if exists ix_rcpa_doctor_month_country_pcode")
    op.execute("drop index if exists ix_rcpa_doctor_month_summary_mapping_provenance")
    op.execute(
        """
        alter table if exists rcpa_doctor_month_summary
        drop constraint if exists rcpa_doctor_month_summary_pkey
        """
    )

    # Doctor detail needs brand mix, not row UUIDs, doctor names, or repeated month metadata.
    op.execute(
        """
        create table rcpa_doctor_brand_summary_slim (
            source_file_id uuid not null references source_files(id),
            country_id uuid not null references countries(id),
            pcode_normalized text not null,
            brand_group text not null,
            own_or_competitor text not null,
            prescription_qty numeric(18, 2) not null,
            prescription_value_local numeric(18, 2),
            currency_code text not null,
            row_count_aggregated integer not null
        )
        """
    )
    op.execute(
        """
        insert into rcpa_doctor_brand_summary_slim (
            source_file_id,
            country_id,
            pcode_normalized,
            brand_group,
            own_or_competitor,
            prescription_qty,
            prescription_value_local,
            currency_code,
            row_count_aggregated
        )
        select
            source_file_id,
            country_id,
            pcode_normalized,
            brand_group,
            own_or_competitor,
            coalesce(prescription_qty, 0),
            prescription_value_local,
            currency_code,
            coalesce(row_count_aggregated, 0)
        from rcpa_doctor_brand_summary
        """
    )
    op.drop_table("rcpa_doctor_brand_summary")
    op.rename_table("rcpa_doctor_brand_summary_slim", "rcpa_doctor_brand_summary")
    op.create_index(
        "ix_rcpa_doctor_brand_summary_lookup",
        "rcpa_doctor_brand_summary",
        ["country_id", "pcode_normalized", "brand_group"],
    )
    op.create_index(
        "ix_rcpa_doctor_brand_summary_brand",
        "rcpa_doctor_brand_summary",
        ["brand_group"],
    )
    op.execute("analyze rcpa_doctor_month_summary")
    op.execute("analyze rcpa_doctor_brand_summary")
    op.execute("analyze doctors")
    op.execute("analyze doctor_engagement_facts")


def downgrade() -> None:
    op.drop_index(
        "ix_rcpa_doctor_brand_summary_brand",
        table_name="rcpa_doctor_brand_summary",
    )
    op.drop_index(
        "ix_rcpa_doctor_brand_summary_lookup",
        table_name="rcpa_doctor_brand_summary",
    )
    op.drop_table("rcpa_doctor_brand_summary")
    op.execute(
        """
        create table rcpa_doctor_brand_summary (
            id uuid primary key default uuid_generate_v4(),
            source_file_id uuid not null references source_files(id),
            ingestion_run_id uuid references ingestion_runs(id),
            country_id uuid not null references countries(id),
            first_calendar_month_id uuid references calendar_months(id),
            last_calendar_month_id uuid references calendar_months(id),
            pcode_normalized text not null,
            doctor_name text,
            brand_group text not null,
            own_or_competitor text not null,
            prescription_qty numeric(18, 2) not null,
            prescription_value_local numeric(18, 2),
            currency_code text not null,
            row_count_aggregated integer not null
        )
        """
    )
    op.create_index(
        "ix_rcpa_doctor_brand_summary_pcode",
        "rcpa_doctor_brand_summary",
        ["country_id", "pcode_normalized"],
    )
    op.execute(
        """
        alter table if exists rcpa_doctor_month_summary
        add constraint rcpa_doctor_month_summary_pkey primary key (id)
        """
    )
    op.create_index(
        "ix_rcpa_doctor_month_country_pcode",
        "rcpa_doctor_month_summary",
        ["country_id", "calendar_month_id", "pcode_normalized"],
    )
    op.create_index(
        "ix_rcpa_doctor_month_summary_mapping_provenance",
        "rcpa_doctor_month_summary",
        ["mapping_provenance"],
    )
    op.execute(
        """
        create table doctor_master_mappings (
            id uuid primary key default uuid_generate_v4(),
            source_file_id uuid not null references source_files(id),
            ingestion_run_id uuid not null references ingestion_runs(id),
            country_id uuid not null references countries(id),
            pcode_raw text,
            pcode_normalized text not null,
            doctor_name text not null,
            doctor_short_name text,
            doctor_name_normalized text not null,
            territory_name text,
            territory_id text,
            patch text,
            patch_name text,
            legacy_code text,
            speciality text,
            doctor_class text,
            taskforce text,
            rep_name text,
            rep_code text,
            employee_id text,
            manager_name text,
            town text,
            cis_no text,
            registration_no text,
            gender text,
            source_sheet_name text not null,
            source_row_number integer not null,
            source_row_hash text not null,
            created_at timestamp with time zone not null default now(),
            constraint uq_doctor_master_mappings_source_row_hash
                unique (source_file_id, source_row_hash)
        )
        """
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
