from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from backend.app.main import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def migration_files() -> list[str]:
    return [
        "0001_base_schema.py",
        "0002_audit_source_tables.py",
        "0003_reference_tables.py",
        "0004_canonical_tables.py",
        "0005_reconciliation_ai_tables.py",
        "0006_indexes_constraints.py",
        "0007_phase_1_3_schema_completion.py",
        "0008_supabase_free_tier_rcpa_storage.py",
        "0009_drop_obsolete_rcpa_prescriptions.py",
        "0010_execution_governance_views.py",
        "0011_phase4_execution_matrix_fixes.py",
        "0012_phase4_real_data_repairs.py",
    ]


@pytest.fixture
def alembic_config() -> Config:
    config_path = Path("alembic.ini")
    assert config_path.exists(), "alembic.ini must exist before migration tests run"
    return Config(str(config_path))


def reset_database(alembic_config: Config) -> None:
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")
