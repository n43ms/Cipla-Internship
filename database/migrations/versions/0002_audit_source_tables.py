"""audit and source tables

Revision ID: 0002_audit_source_tables
Revises: 0001_base_schema
Create Date: 2026-06-16
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0002_audit_source_tables"
down_revision: str | None = "0001_base_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def uuid_pk() -> sa.Column:
    return sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()"))


def upgrade() -> None:
    op.create_table(
        "ingestion_runs",
        uuid_pk(),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("triggered_by", sa.Text()),
        sa.Column("source_file_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_rows_seen", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_rows_loaded", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_rows_skipped", sa.Integer(), server_default="0", nullable=False),
        sa.Column("warning_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("summary_json", sa.JSON()),
        sa.CheckConstraint(
            "status IN ('running', 'completed', 'completed_with_warnings', 'failed')",
            name="ck_ingestion_runs_status",
        ),
    )
    op.create_table(
        "source_files",
        uuid_pk(),
        sa.Column("original_filename", sa.Text(), nullable=False),
        sa.Column("file_hash", sa.Text(), nullable=False),
        sa.Column("file_type", sa.Text(), nullable=False),
        sa.Column("source_type", sa.Text(), nullable=False),
        sa.Column("country_scope", sa.Text()),
        sa.Column("period_start", sa.Date()),
        sa.Column("period_end", sa.Date()),
        sa.Column("detected_sheet_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("file_hash", name="uq_source_files_file_hash"),
    )
    op.create_table(
        "ingestion_run_files",
        uuid_pk(),
        sa.Column("ingestion_run_id", sa.UUID(), sa.ForeignKey("ingestion_runs.id"), nullable=False),
        sa.Column("source_file_id", sa.UUID(), sa.ForeignKey("source_files.id"), nullable=False),
        sa.Column("local_path_snapshot", sa.Text()),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("sheets_profiled", sa.Integer(), server_default="0", nullable=False),
        sa.Column("rows_seen", sa.Integer(), server_default="0", nullable=False),
        sa.Column("rows_loaded", sa.Integer(), server_default="0", nullable=False),
        sa.Column("rows_skipped", sa.Integer(), server_default="0", nullable=False),
        sa.Column("warnings", sa.Integer(), server_default="0", nullable=False),
        sa.Column("errors", sa.Integer(), server_default="0", nullable=False),
        sa.Column("profile_json", sa.JSON()),
        sa.UniqueConstraint("ingestion_run_id", "source_file_id", name="uq_ingestion_run_files_run_file"),
    )
    op.create_table(
        "validation_errors",
        uuid_pk(),
        sa.Column("ingestion_run_id", sa.UUID(), sa.ForeignKey("ingestion_runs.id"), nullable=False),
        sa.Column("source_file_id", sa.UUID(), sa.ForeignKey("source_files.id")),
        sa.Column("sheet_name", sa.Text()),
        sa.Column("row_number", sa.Integer()),
        sa.Column("severity", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.Text()),
        sa.Column("field_name", sa.Text()),
        sa.Column("error_code", sa.Text(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("raw_value", sa.Text()),
        sa.CheckConstraint("severity IN ('info', 'warning', 'error')", name="ck_validation_errors_severity"),
    )


def downgrade() -> None:
    op.drop_table("validation_errors")
    op.drop_table("ingestion_run_files")
    op.drop_table("source_files")
    op.drop_table("ingestion_runs")
