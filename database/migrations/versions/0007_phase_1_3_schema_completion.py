"""complete phase 1-3 canonical schema

Revision ID: 0007_phase_1_3_schema_completion
Revises: 0006_indexes_constraints
Create Date: 2026-06-16
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0007_phase_1_3_schema_completion"
down_revision: str | None = "0006_indexes_constraints"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _add_columns(
        "plan_events",
        [
            sa.Column("planned_honorarium_hcps", sa.Integer()),
            sa.Column("planned_delegate_hcps", sa.Integer()),
            sa.Column("honorarium_cost_per_hcp_usd", sa.Numeric(18, 2)),
            sa.Column("total_honorarium_cost_usd", sa.Numeric(18, 2)),
            sa.Column("operational_cost_per_unit_usd", sa.Numeric(18, 2)),
            sa.Column("total_operational_cost_usd", sa.Numeric(18, 2)),
            sa.Column("comments", sa.Text()),
            sa.Column("country_comment", sa.Text()),
            sa.Column("ho_finalized", sa.Text()),
        ],
    )
    _add_columns(
        "execution_snapshots",
        [
            sa.Column("yp_total_doctors", sa.Integer()),
            sa.Column("raised_total_doctors", sa.Integer()),
            sa.Column("approved_total_doctors", sa.Integer()),
            sa.Column("request_total_doctors", sa.Integer()),
            sa.Column("event_created_count", sa.Integer()),
        ],
    )
    _add_columns(
        "execution_requests",
        [
            sa.Column("topic_remarks", sa.Text()),
            sa.Column("association_contract_id", sa.Text()),
            sa.Column("association_deliverables", sa.Text()),
            sa.Column("fx_rate_source", sa.Text()),
            sa.Column("fx_rate_date", sa.Date()),
            sa.Column("estimated_intervention_usd", sa.Numeric(18, 2)),
            sa.Column("confirmed_contracted_amount_usd", sa.Numeric(18, 2)),
            sa.Column("actual_total_expense_usd", sa.Numeric(18, 2)),
            sa.Column("actual_btu_expense_usd", sa.Numeric(18, 2)),
            sa.Column("actual_btc_expense_usd", sa.Numeric(18, 2)),
            sa.Column("direct_hcp_spend_local", sa.Numeric(18, 2)),
            sa.Column("overhead_spend_local", sa.Numeric(18, 2)),
            sa.Column("total_roi_spend_local", sa.Numeric(18, 2)),
            sa.Column("direct_hcp_spend_usd", sa.Numeric(18, 2)),
            sa.Column("overhead_spend_usd", sa.Numeric(18, 2)),
            sa.Column("total_roi_spend_usd", sa.Numeric(18, 2)),
            sa.Column("expected_customer_count", sa.Integer()),
            sa.Column("attended_customer_count", sa.Integer()),
            sa.Column("expected_category_raw", sa.Text()),
            sa.Column("attended_category_raw", sa.Text()),
            sa.Column("expense_submitted_date", sa.Date()),
            sa.Column("expense_confirmed_date", sa.Date()),
            sa.Column("approval_status", sa.Text()),
            sa.Column("confirmation_status", sa.Text()),
            sa.Column("cancellation_reason", sa.Text()),
            sa.Column("city", sa.Text()),
            sa.Column("state", sa.Text()),
        ],
    )
    _add_columns(
        "doctors",
        [
            sa.Column("first_seen_month_id", sa.UUID(), sa.ForeignKey("calendar_months.id")),
            sa.Column("last_seen_month_id", sa.UUID(), sa.ForeignKey("calendar_months.id")),
        ],
    )
    _add_columns(
        "rcpa_prescriptions",
        [
            sa.Column("speciality", sa.Text()),
            sa.Column("doctor_class", sa.Text()),
            sa.Column("patch_name", sa.Text()),
            sa.Column("active_status", sa.Text()),
            sa.Column("sku_detail", sa.Text()),
        ],
    )
    op.execute("UPDATE request_doctors SET parse_status = 'parsed' WHERE parse_status = 'ok'")
    op.create_check_constraint(
        "ck_execution_snapshots_snapshot_source",
        "execution_snapshots",
        "snapshot_source IN ('monthly_planner', 'derived_from_consolidation')",
    )
    op.create_check_constraint(
        "ck_execution_snapshots_normalized_status",
        "execution_snapshots",
        "normalized_status IN ('executed', 'action_due', 'unknown')",
    )
    op.create_check_constraint(
        "ck_request_doctors_attendance_type",
        "request_doctors",
        "attendance_type IN ('expected', 'actual')",
    )
    op.create_check_constraint(
        "ck_request_doctors_parse_status",
        "request_doctors",
        "parse_status IN ('parsed', 'missing_pcode', 'ambiguous', 'invalid')",
    )
    op.create_check_constraint(
        "ck_execution_requests_fx_rate_status",
        "execution_requests",
        "fx_rate_status IN ('official', 'provisional', 'missing')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_execution_requests_fx_rate_status", "execution_requests", type_="check")
    op.drop_constraint("ck_request_doctors_parse_status", "request_doctors", type_="check")
    op.drop_constraint("ck_request_doctors_attendance_type", "request_doctors", type_="check")
    op.drop_constraint("ck_execution_snapshots_normalized_status", "execution_snapshots", type_="check")
    op.drop_constraint("ck_execution_snapshots_snapshot_source", "execution_snapshots", type_="check")
    for table_name, columns in {
        "rcpa_prescriptions": ["sku_detail", "active_status", "patch_name", "doctor_class", "speciality"],
        "doctors": ["last_seen_month_id", "first_seen_month_id"],
        "execution_requests": [
            "state",
            "city",
            "cancellation_reason",
            "confirmation_status",
            "approval_status",
            "expense_confirmed_date",
            "expense_submitted_date",
            "attended_category_raw",
            "expected_category_raw",
            "attended_customer_count",
            "expected_customer_count",
            "total_roi_spend_usd",
            "overhead_spend_usd",
            "direct_hcp_spend_usd",
            "total_roi_spend_local",
            "overhead_spend_local",
            "direct_hcp_spend_local",
            "actual_btc_expense_usd",
            "actual_btu_expense_usd",
            "actual_total_expense_usd",
            "confirmed_contracted_amount_usd",
            "estimated_intervention_usd",
            "fx_rate_date",
            "fx_rate_source",
            "association_deliverables",
            "association_contract_id",
            "topic_remarks",
        ],
        "execution_snapshots": [
            "event_created_count",
            "request_total_doctors",
            "approved_total_doctors",
            "raised_total_doctors",
            "yp_total_doctors",
        ],
        "plan_events": [
            "ho_finalized",
            "country_comment",
            "comments",
            "total_operational_cost_usd",
            "operational_cost_per_unit_usd",
            "total_honorarium_cost_usd",
            "honorarium_cost_per_hcp_usd",
            "planned_delegate_hcps",
            "planned_honorarium_hcps",
        ],
    }.items():
        for column in columns:
            op.drop_column(table_name, column)


def _add_columns(table_name: str, columns: list[sa.Column]) -> None:
    for column in columns:
        op.add_column(table_name, column)
