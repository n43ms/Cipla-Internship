from __future__ import annotations

from ingestion.loaders.consolidation import load_consolidation
from ingestion.models import LoadResult, WorkbookProfile


def load_consolidated_intervention(profile: WorkbookProfile) -> LoadResult:
    """Load the raw consolidated intervention export into the request spine."""
    return load_consolidation(profile)
