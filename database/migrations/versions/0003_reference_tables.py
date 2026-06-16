"""reference tables

Revision ID: 0003_reference_tables
Revises: 0002_audit_source_tables
Create Date: 2026-06-16
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0003_reference_tables"
down_revision: str | None = "0002_audit_source_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def uuid_pk() -> sa.Column:
    return sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()"))


def upgrade() -> None:
    op.create_table(
        "countries",
        uuid_pk(),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("default_currency_code", sa.Text(), nullable=False),
        sa.UniqueConstraint("code", name="uq_countries_code"),
    )
    op.create_table(
        "calendar_months",
        uuid_pk(),
        sa.Column("month_start_date", sa.Date(), nullable=False),
        sa.Column("month_label", sa.Text(), nullable=False),
        sa.Column("fiscal_year", sa.Text(), nullable=False),
        sa.Column("fiscal_month_number", sa.Integer(), nullable=False),
        sa.Column("calendar_year", sa.Integer(), nullable=False),
        sa.Column("calendar_month_number", sa.Integer(), nullable=False),
        sa.UniqueConstraint("month_start_date", name="uq_calendar_months_start"),
    )
    op.create_table(
        "exchange_rates",
        uuid_pk(),
        sa.Column("currency_code", sa.Text(), nullable=False),
        sa.Column("rate_to_usd", sa.Numeric(18, 10)),
        sa.Column("rate_date", sa.Date()),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("rate_status", sa.Text(), nullable=False),
        sa.UniqueConstraint("currency_code", "rate_date", "source", name="uq_exchange_rates_currency_date_source"),
        sa.CheckConstraint("rate_status IN ('official', 'provisional', 'missing')", name="ck_exchange_rate_status"),
    )


def downgrade() -> None:
    op.drop_table("exchange_rates")
    op.drop_table("calendar_months")
    op.drop_table("countries")
