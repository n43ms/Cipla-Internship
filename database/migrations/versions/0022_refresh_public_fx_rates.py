"""refresh provisional public fx rates

Revision ID: 0022_refresh_public_fx
Revises: 0021_cleanup_fx_seeds
Create Date: 2026-06-19
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0022_refresh_public_fx"
down_revision: str | None = "0021_cleanup_fx_seeds"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        insert into exchange_rates (currency_code, rate_to_usd, rate_date, source, rate_status)
        values
          ('NPR', 1.0 / 151.06361, '2026-06-19', 'public_market_rate', 'provisional'),
          ('MMK', 1.0 / 2104.074172, '2026-06-19', 'public_market_rate', 'provisional'),
          ('OMR', 1.0 / 0.384497, '2026-06-19', 'public_market_rate', 'provisional'),
          ('AED', 1.0 / 3.6725, '2026-06-19', 'public_market_rate', 'provisional'),
          ('MYR', 1.0 / 4.114387, '2026-06-19', 'public_market_rate', 'provisional')
        on conflict (currency_code, rate_date, source) do update
        set
          rate_to_usd = excluded.rate_to_usd,
          rate_status = excluded.rate_status
        """
    )
    _recompute_provisional_request_usd()
    _refresh_views()


def downgrade() -> None:
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
    _recompute_provisional_request_usd()
    _refresh_views()


def _recompute_provisional_request_usd() -> None:
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
            confirmed_vs_estimated_variance_usd = round(er.confirmed_vs_estimated_variance_local * rates.rate_to_usd, 2),
            actual_total_expense_usd = round(er.actual_total_expense_local * rates.rate_to_usd, 2),
            actual_btu_expense_usd = round(er.actual_btu_expense_local * rates.rate_to_usd, 2),
            actual_btc_expense_usd = round(er.actual_btc_expense_local * rates.rate_to_usd, 2),
            direct_hcp_spend_usd = round(er.direct_hcp_spend_local * rates.rate_to_usd, 2),
            overhead_spend_usd = round(er.overhead_spend_local * rates.rate_to_usd, 2),
            total_roi_spend_usd = round(er.total_roi_spend_local * rates.rate_to_usd, 2)
        from rates
        where er.currency_code = rates.currency_code
          and er.currency_code in ('NPR', 'MMK', 'OMR', 'AED', 'MYR')
        """
    )


def _refresh_views() -> None:
    for view_name in [
        "mv_budget_utilization",
        "mv_doctor_roi",
        "mv_intervention_mix",
        "mv_data_quality",
    ]:
        op.execute(f"refresh materialized view {view_name}")
