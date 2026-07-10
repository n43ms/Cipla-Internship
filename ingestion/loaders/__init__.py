"""Source-specific workbook loaders."""

from ingestion.loaders.consolidated_intervention import load_consolidated_intervention
from ingestion.loaders.consolidation import load_consolidation
from ingestion.loaders.doctor_wise_intervention import load_doctor_wise_intervention
from ingestion.loaders.ers_conference import load_ers_conference
from ingestion.loaders.execution_snapshot import load_execution_snapshot
from ingestion.loaders.planner import load_planner
from ingestion.loaders.rcpa import load_rcpa

__all__ = [
    "load_consolidated_intervention",
    "load_consolidation",
    "load_doctor_wise_intervention",
    "load_ers_conference",
    "load_execution_snapshot",
    "load_planner",
    "load_rcpa",
]

