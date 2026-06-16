"""base schema

Revision ID: 0001_base_schema
Revises:
Create Date: 2026-06-16
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0001_base_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute(
        """
        DO $$
        BEGIN
            CREATE TYPE ingestion_status AS ENUM (
                'running', 'completed', 'completed_with_warnings', 'failed'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            CREATE TYPE validation_severity AS ENUM ('info', 'warning', 'error');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP TYPE IF EXISTS validation_severity")
    op.execute("DROP TYPE IF EXISTS ingestion_status")
