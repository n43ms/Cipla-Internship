"""add provisional public fx rates

Revision ID: 0020_public_fx_rates
Revises: 0019_phase5_7_fix
Create Date: 2026-06-19
"""

from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0020_public_fx_rates"
down_revision: str | None = "0019_phase5_7_fix"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        insert into exchange_rates (currency_code, rate_to_usd, rate_date, source, rate_status)
        values
          ('NPR', 1.0 / 150.94, '2026-06-19', 'public_market_rate', 'provisional'),
          ('MMK', 1.0 / 2098.58, '2026-06-19', 'public_market_rate', 'provisional'),
          ('OMR', 1.0 / 0.384985, '2026-06-19', 'public_market_rate', 'provisional'),
          ('AED', 1.0 / 3.6725, '2026-06-19', 'public_market_rate', 'provisional'),
          ('MYR', 1.0 / 4.1390, '2026-06-19', 'public_market_rate', 'provisional')
        on conflict (currency_code, rate_date, source) do update
        set
          rate_to_usd = excluded.rate_to_usd,
          rate_status = excluded.rate_status
        """
    )
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
            where source = 'public_market_rate'
              and rate_status = 'provisional'
              and rate_to_usd is not null
            order by currency_code, rate_date desc
        )
        update execution_requests er
        set
            fx_rate_to_usd = rates.rate_to_usd,
            fx_rate_source = rates.source,
            fx_rate_date = rates.rate_date,
            fx_rate_status = rates.rate_status,
            estimated_intervention_usd = round(er.estimated_intervention_local * rates.rate_to_usd, 2),
            confirmed_contracted_amount_usd = round(er.confirmed_contracted_amount_local * rates.rate_to_usd, 2),
            actual_total_expense_usd = round(er.actual_total_expense_local * rates.rate_to_usd, 2),
            actual_btu_expense_usd = round(er.actual_btu_expense_local * rates.rate_to_usd, 2),
            actual_btc_expense_usd = round(er.actual_btc_expense_local * rates.rate_to_usd, 2),
            direct_hcp_spend_usd = round(er.direct_hcp_spend_local * rates.rate_to_usd, 2),
            overhead_spend_usd = round(er.overhead_spend_local * rates.rate_to_usd, 2),
            total_roi_spend_usd = round(er.total_roi_spend_local * rates.rate_to_usd, 2)
        from rates
        where er.currency_code = rates.currency_code
          and er.fx_rate_status = 'missing'
        """
    )
    op.execute("drop materialized view if exists mv_data_quality")
    op.execute(_read_view_sql("mv_data_quality.sql"))
    op.create_index("ix_mv_data_quality_latest_run", "mv_data_quality", ["latest_ingestion_run_id"])
    _refresh_views()


def downgrade() -> None:
    op.execute(
        """
        update execution_requests
        set
            fx_rate_to_usd = null,
            fx_rate_source = 'pending_company_rate',
            fx_rate_date = null,
            fx_rate_status = 'missing',
            estimated_intervention_usd = null,
            confirmed_contracted_amount_usd = null,
            actual_total_expense_usd = null,
            actual_btu_expense_usd = null,
            actual_btc_expense_usd = null,
            direct_hcp_spend_usd = null,
            overhead_spend_usd = null,
            total_roi_spend_usd = null
        where fx_rate_source = 'public_market_rate'
          and currency_code in ('NPR', 'MMK', 'OMR', 'AED', 'MYR')
        """
    )
    op.execute("delete from exchange_rates where source = 'public_market_rate'")
    op.execute("drop materialized view if exists mv_data_quality")
    op.execute(_read_view_sql("mv_data_quality.sql"))
    op.create_index("ix_mv_data_quality_latest_run", "mv_data_quality", ["latest_ingestion_run_id"])
    _refresh_views()


def _refresh_views() -> None:
    for view_name in [
        "mv_budget_utilization",
        "mv_doctor_roi",
        "mv_intervention_mix",
        "mv_data_quality",
    ]:
        op.execute(f"refresh materialized view {view_name}")


def _read_view_sql(file_name: str) -> str:
    return (Path(__file__).resolve().parents[2] / "views" / file_name).read_text(encoding="utf-8")
