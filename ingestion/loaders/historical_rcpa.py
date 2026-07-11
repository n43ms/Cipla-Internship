from __future__ import annotations

from ingestion.loaders.rcpa import load_rcpa
from ingestion.models import LoadResult, WorkbookProfile


def load_historical_rcpa(profile: WorkbookProfile) -> LoadResult:
    result = load_rcpa(profile)
    result.summaries["rcpa_load_mode"] = "historical_backfill"
    return result
