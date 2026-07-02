"""cleanup pending fx seed rows

Revision ID: 0021_cleanup_fx_seeds
Revises: 0020_public_fx_rates
Create Date: 2026-06-19
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0021_cleanup_fx_seeds"
down_revision: str | None = "0020_public_fx_rates"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        delete from exchange_rates
        where source = 'pending_company_rate'
          and rate_status = 'missing'
          and currency_code in ('NPR', 'MMK', 'OMR', 'AED', 'MYR')
        """
    )
    op.execute("refresh materialized view mv_data_quality")


def downgrade() -> None:
    op.execute(
        """
        insert into exchange_rates (currency_code, rate_to_usd, rate_date, source, rate_status)
        values
          ('NPR', null, null, 'pending_company_rate', 'missing'),
          ('MMK', null, null, 'pending_company_rate', 'missing'),
          ('OMR', null, null, 'pending_company_rate', 'missing'),
          ('AED', null, null, 'pending_company_rate', 'missing'),
          ('MYR', null, null, 'pending_company_rate', 'missing')
        on conflict (currency_code, rate_date, source) do update
        set rate_to_usd = excluded.rate_to_usd,
            rate_status = excluded.rate_status
        """
    )
    op.execute("refresh materialized view mv_data_quality")
