"""canonical business tables

Revision ID: 0004_canonical_tables
Revises: 0003_reference_tables
Create Date: 2026-06-16
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0004_canonical_tables"
down_revision: str | None = "0003_reference_tables"
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
    op.create_table(
        "plan_events",
        uuid_pk(),
        *source_cols(),
        sa.Column("country_id", sa.UUID(), sa.ForeignKey("countries.id"), nullable=False),
        sa.Column("calendar_month_id", sa.UUID(), sa.ForeignKey("calendar_months.id"), nullable=False),
        sa.Column("fiscal_year", sa.Text()),
        sa.Column("therapy", sa.Text()),
        sa.Column("event_type", sa.Text()),
        sa.Column("event_name", sa.Text(), nullable=False),
        sa.Column("event_name_normalized", sa.Text(), nullable=False),
        sa.Column("central_or_local", sa.Text()),
        sa.Column("brand_name_1", sa.Text()),
        sa.Column("brand_name_2", sa.Text()),
        sa.Column("planned_total_hcps", sa.Integer()),
        sa.Column("planned_patients", sa.Integer()),
        sa.Column("planned_pharmacies", sa.Integer()),
        sa.Column("total_planned_cost_usd", sa.Numeric(18, 2)),
        sa.Column("source_sheet_name", sa.Text(), nullable=False),
        sa.Column("source_row_number", sa.Integer(), nullable=False),
    )
    op.create_table(
        "execution_snapshots",
        uuid_pk(),
        *source_cols(),
        sa.Column("country_id", sa.UUID(), sa.ForeignKey("countries.id"), nullable=False),
        sa.Column("calendar_month_id", sa.UUID(), sa.ForeignKey("calendar_months.id"), nullable=False),
        sa.Column("therapy", sa.Text()),
        sa.Column("event_type", sa.Text()),
        sa.Column("event_name", sa.Text(), nullable=False),
        sa.Column("event_name_normalized", sa.Text(), nullable=False),
        sa.Column("planned_hcps", sa.Integer()),
        sa.Column("engaged_hcps", sa.Integer()),
        sa.Column("raised_request_count", sa.Integer()),
        sa.Column("snapshot_source", sa.Text(), nullable=False),
        sa.Column("status_source_value", sa.Text()),
        sa.Column("normalized_status", sa.Text(), nullable=False),
        sa.Column("source_sheet_name", sa.Text(), nullable=False),
        sa.Column("source_row_number", sa.Integer(), nullable=False),
    )
    op.create_table(
        "execution_requests",
        uuid_pk(),
        *source_cols(),
        sa.Column("source_system", sa.Text(), nullable=False, server_default="consolidation"),
        sa.Column("req_id", sa.Text()),
        sa.Column("request_uid", sa.Text(), nullable=False),
        sa.Column("country_id", sa.UUID(), sa.ForeignKey("countries.id"), nullable=False),
        sa.Column("calendar_month_id", sa.UUID(), sa.ForeignKey("calendar_months.id"), nullable=False),
        sa.Column("rep_code", sa.Text()),
        sa.Column("rep_name", sa.Text()),
        sa.Column("intervention_date", sa.Date()),
        sa.Column("actual_intervention_date", sa.Date()),
        sa.Column("venue", sa.Text()),
        sa.Column("intervention_name", sa.Text(), nullable=False),
        sa.Column("intervention_name_normalized", sa.Text(), nullable=False),
        sa.Column("intervention_type", sa.Text()),
        sa.Column("intervention_sub_type", sa.Text()),
        sa.Column("estimated_intervention_local", sa.Numeric(18, 2)),
        sa.Column("confirmed_contracted_amount_local", sa.Numeric(18, 2)),
        sa.Column("confirmed_vs_estimated_variance_local", sa.Numeric(18, 2)),
        sa.Column("actual_total_expense_local", sa.Numeric(18, 2)),
        sa.Column("actual_btu_expense_local", sa.Numeric(18, 2)),
        sa.Column("actual_btc_expense_local", sa.Numeric(18, 2)),
        sa.Column("association_amount_local", sa.Numeric(18, 2)),
        sa.Column("currency_code", sa.Text(), nullable=False),
        sa.Column("fx_rate_to_usd", sa.Numeric(18, 10)),
        sa.Column("fx_rate_status", sa.Text(), nullable=False),
        sa.Column("request_approval_status", sa.Text()),
        sa.Column("request_confirmation_status", sa.Text()),
        sa.Column("post_approval_status", sa.Text()),
        sa.Column("post_confirmation_status", sa.Text()),
        sa.Column("current_owner_stage", sa.Text()),
        sa.Column("approval_chain_json", sa.JSON()),
        sa.Column("source_row_number", sa.Integer(), nullable=False),
        sa.UniqueConstraint("source_system", "req_id", name="uq_execution_requests_source_req_id"),
        sa.UniqueConstraint("request_uid", name="uq_execution_requests_request_uid"),
    )
    op.create_table(
        "request_doctors",
        uuid_pk(),
        sa.Column("execution_request_id", sa.UUID(), sa.ForeignKey("execution_requests.id"), nullable=False),
        sa.Column("attendance_type", sa.Text(), nullable=False),
        sa.Column("doctor_name_raw", sa.Text()),
        sa.Column("doctor_class_raw", sa.Text()),
        sa.Column("pcode_raw", sa.Text()),
        sa.Column("pcode_normalized", sa.Text()),
        sa.Column("parse_status", sa.Text(), nullable=False),
        sa.Column("source_position", sa.Integer(), nullable=False),
        sa.UniqueConstraint(
            "execution_request_id",
            "attendance_type",
            "source_position",
            name="uq_request_doctors_request_type_position",
        ),
    )
    op.create_table(
        "doctors",
        uuid_pk(),
        sa.Column("country_id", sa.UUID(), sa.ForeignKey("countries.id"), nullable=False),
        sa.Column("pcode_normalized", sa.Text(), nullable=False),
        sa.Column("latest_doctor_name", sa.Text()),
        sa.Column("speciality", sa.Text()),
        sa.Column("doctor_class", sa.Text()),
        sa.Column("patch_name", sa.Text()),
        sa.Column("active_status", sa.Text()),
        sa.Column("source_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("country_id", "pcode_normalized", name="uq_doctors_country_pcode"),
    )
    op.create_table(
        "rcpa_prescriptions",
        uuid_pk(),
        *source_cols(),
        sa.Column("country_id", sa.UUID(), sa.ForeignKey("countries.id"), nullable=False),
        sa.Column("calendar_month_id", sa.UUID(), sa.ForeignKey("calendar_months.id"), nullable=False),
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
    )


def downgrade() -> None:
    op.drop_table("rcpa_prescriptions")
    op.drop_table("doctors")
    op.drop_table("request_doctors")
    op.drop_table("execution_requests")
    op.drop_table("execution_snapshots")
    op.drop_table("plan_events")
