"""doctor engagement facts and company FX refresh

Revision ID: 0023_doctor_engagement_facts
Revises: 0022_refresh_public_fx
Create Date: 2026-07-10
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0023_doctor_engagement_facts"
down_revision: str | None = "0022_refresh_public_fx"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("drop materialized view if exists mv_data_quality")
    op.execute("drop materialized view if exists mv_doctor_roi")
    op.execute(
        """
        create table if not exists doctor_engagement_facts (
            id uuid primary key default uuid_generate_v4(),
            source_file_id uuid not null references source_files(id),
            ingestion_run_id uuid not null references ingestion_runs(id),
            country_id uuid not null references countries(id),
            calendar_month_id uuid not null references calendar_months(id),
            region text,
            territory_code text,
            fs_hq text,
            request_date date,
            expected_intervention_date date,
            intervention_id text not null,
            intervention_name text,
            intervention_name_normalized text,
            intervention_type text,
            intervention_subtype text,
            pcode_raw text,
            pcode_normalized text,
            doctor_segment text,
            doctor_name text not null,
            estimated_intervention_amount_local numeric(18, 2),
            btu_expense_local numeric(18, 2),
            expense_against_advance_local numeric(18, 2),
            btc_expense_local numeric(18, 2),
            total_actual_intervention_expense_local numeric(18, 2),
            fmv_speciality text,
            fmv_tier text,
            fmv_role text,
            fmv_amount_local numeric(18, 2),
            contract_id text,
            contracted_amount_local numeric(18, 2),
            contract_saving_local numeric(18, 2),
            status text,
            is_sponsorship boolean not null default false,
            sponsorship_class text,
            engagement_class text not null default 'unclassified',
            classification_reason text,
            classification_confidence numeric(5, 2),
            currency_code text not null,
            fx_rate_to_usd numeric(18, 10),
            fx_rate_source text,
            fx_rate_date date,
            fx_rate_status text not null,
            fmv_amount_usd numeric(18, 2),
            contracted_amount_usd numeric(18, 2),
            contract_saving_usd numeric(18, 2),
            source_sheet_name text not null,
            source_row_number integer not null,
            source_row_hash text not null,
            constraint uq_doctor_engagement_source_row_hash unique (source_file_id, source_row_hash)
        )
        """
    )
    op.create_index(
        "ix_doctor_engagement_country_pcode",
        "doctor_engagement_facts",
        ["country_id", "pcode_normalized"],
    )
    op.create_index(
        "ix_doctor_engagement_intervention_id",
        "doctor_engagement_facts",
        ["intervention_id"],
    )
    op.execute(
        """
        alter table doctor_engagement_facts
          add column if not exists is_sponsorship boolean not null default false,
          add column if not exists sponsorship_class text,
          add column if not exists engagement_class text not null default 'unclassified',
          add column if not exists classification_reason text,
          add column if not exists classification_confidence numeric(5, 2)
        """
    )
    _seed_company_fx_rates()
    _recompute_company_fx_request_usd()
    op.execute(_read_view_sql("mv_doctor_roi.sql"))
    op.create_index(
        "ix_mv_doctor_roi_country_pcode",
        "mv_doctor_roi",
        ["country_id", "pcode_normalized"],
    )
    op.create_index("ix_mv_doctor_roi_segment", "mv_doctor_roi", ["roi_segment"])
    op.create_index("ix_mv_doctor_roi_quadrant", "mv_doctor_roi", ["quadrant_label"])
    op.create_index(
        "ix_mv_doctor_roi_engagement_window",
        "mv_doctor_roi",
        ["first_engagement_date", "last_engagement_date"],
    )
    op.execute("refresh materialized view mv_doctor_roi")


def downgrade() -> None:
    op.execute("drop materialized view if exists mv_data_quality")
    op.execute("drop materialized view if exists mv_doctor_roi")
    op.execute("drop table if exists doctor_engagement_facts")
    op.execute(_read_view_sql("mv_doctor_roi.sql"))
    op.execute(_read_view_sql("mv_data_quality.sql"))


def _seed_company_fx_rates() -> None:
    op.execute(
        """
        delete from exchange_rates
        where source = 'public_market_rate'
          and currency_code in ('LKR', 'NPR', 'OMR', 'AED', 'MMK', 'MYR')
        """
    )
    op.execute(
        """
        insert into exchange_rates (currency_code, rate_to_usd, rate_date, source, rate_status)
        values
          ('LKR', 1.0 / 368.90, '2026-07-10', 'company', 'official'),
          ('NPR', 1.0 / 89.0, '2026-07-10', 'company', 'official'),
          ('OMR', 1.0 / 0.46, '2026-07-10', 'company', 'official'),
          ('AED', 1.0, '2026-07-10', 'company', 'official'),
          ('MMK', 1.0 / 4300.0, '2026-07-10', 'company', 'official'),
          ('MYR', 1.0 / 4.39, '2026-07-10', 'company', 'official')
        on conflict (currency_code, rate_date, source) do update
        set
          rate_to_usd = excluded.rate_to_usd,
          rate_status = excluded.rate_status
        """
    )


def _recompute_company_fx_request_usd() -> None:
    op.execute(
        """
        with rates as (
            select distinct on (currency_code)
                currency_code,
                rate_to_usd,
                rate_date,
                source,
                rate_status
            from exchange_rates
            where source = 'company'
              and rate_status = 'official'
              and rate_to_usd is not null
            order by currency_code, rate_date desc
        )
        update execution_requests er
        set
            fx_rate_to_usd = rates.rate_to_usd,
            fx_rate_source = rates.source,
            fx_rate_date = rates.rate_date,
            fx_rate_status = rates.rate_status,
            estimated_intervention_usd =
                round(er.estimated_intervention_local * rates.rate_to_usd, 2),
            confirmed_contracted_amount_usd =
                round(er.confirmed_contracted_amount_local * rates.rate_to_usd, 2),
            actual_total_expense_usd = round(er.actual_total_expense_local * rates.rate_to_usd, 2),
            actual_btu_expense_usd = round(er.actual_btu_expense_local * rates.rate_to_usd, 2),
            actual_btc_expense_usd = round(er.actual_btc_expense_local * rates.rate_to_usd, 2),
            direct_hcp_spend_usd = round(er.direct_hcp_spend_local * rates.rate_to_usd, 2),
            overhead_spend_usd = round(er.overhead_spend_local * rates.rate_to_usd, 2),
            total_roi_spend_usd = round(er.total_roi_spend_local * rates.rate_to_usd, 2)
        from rates
        where er.currency_code = rates.currency_code
        """
    )


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(encoding="utf-8")
