"""indexes and uniqueness constraints

Revision ID: 0006_indexes_constraints
Revises: 0005_reconciliation_ai_tables
Create Date: 2026-06-16
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0006_indexes_constraints"
down_revision: str | None = "0005_reconciliation_ai_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index("ix_source_files_source_type", "source_files", ["source_type"])
    op.create_index("ix_validation_errors_run_severity", "validation_errors", ["ingestion_run_id", "severity"])
    op.create_index("ix_plan_events_country_month", "plan_events", ["country_id", "calendar_month_id"])
    op.create_index("ix_execution_snapshots_country_month", "execution_snapshots", ["country_id", "calendar_month_id"])
    op.create_index("ix_execution_requests_country_month", "execution_requests", ["country_id", "calendar_month_id"])
    op.create_index("ix_request_doctors_pcode", "request_doctors", ["pcode_normalized"])
    op.create_index("ix_rcpa_prescriptions_country_month", "rcpa_prescriptions", ["country_id", "calendar_month_id"])
    op.create_index("ix_event_matches_country_month", "event_matches", ["country_id", "calendar_month_id"])
    op.create_unique_constraint(
        "uq_rcpa_aggregate_grain",
        "rcpa_prescriptions",
        [
            "source_file_id",
            "country_id",
            "calendar_month_id",
            "pcode_normalized",
            "brand_group",
            "sku",
            "own_or_competitor",
            "currency_code",
        ],
    )


def downgrade() -> None:
    op.drop_constraint("uq_rcpa_aggregate_grain", "rcpa_prescriptions", type_="unique")
    op.drop_index("ix_event_matches_country_month", table_name="event_matches")
    op.drop_index("ix_rcpa_prescriptions_country_month", table_name="rcpa_prescriptions")
    op.drop_index("ix_request_doctors_pcode", table_name="request_doctors")
    op.drop_index("ix_execution_requests_country_month", table_name="execution_requests")
    op.drop_index("ix_execution_snapshots_country_month", table_name="execution_snapshots")
    op.drop_index("ix_plan_events_country_month", table_name="plan_events")
    op.drop_index("ix_validation_errors_run_severity", table_name="validation_errors")
    op.drop_index("ix_source_files_source_type", table_name="source_files")
