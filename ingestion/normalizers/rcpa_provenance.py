from __future__ import annotations

from dataclasses import dataclass
from datetime import date

SYSTEM_PCODE_CUTOFF = date(2025, 11, 1)


@dataclass(frozen=True)
class RcpaProvenance:
    mapping_provenance: str
    mapping_note: str


def rcpa_mapping_provenance(
    *,
    month_start_date: date | None,
    pcode_present: bool,
    source_mapping_method: object = None,
) -> RcpaProvenance:
    explicit = _normalize_explicit_method(source_mapping_method)
    if explicit:
        return explicit
    if not pcode_present:
        return RcpaProvenance(
            mapping_provenance="unknown",
            mapping_note="P-code is missing, so doctor mapping provenance cannot be established.",
        )
    if month_start_date is None:
        return RcpaProvenance(
            mapping_provenance="unknown",
            mapping_note="RCPA month is missing, so manual/system mapping cutoff cannot be applied.",
        )
    if month_start_date < SYSTEM_PCODE_CUTOFF:
        return RcpaProvenance(
            mapping_provenance="manual_legacy",
            mapping_note="Historical RCPA before 2025-11-01 uses manual P-code mapping per business clarification.",
        )
    return RcpaProvenance(
        mapping_provenance="system_supplied",
        mapping_note="RCPA month is on or after 2025-11-01 and P-code is source-provided.",
    )


def _normalize_explicit_method(value: object) -> RcpaProvenance | None:
    text = "" if value is None else str(value).strip().lower().replace("-", "_").replace(" ", "_")
    if not text:
        return None
    if text in {"manual", "manual_legacy", "legacy_manual"}:
        return RcpaProvenance("manual_legacy", "Source marks the P-code mapping as manual.")
    if text in {"system", "system_supplied", "system_generated"}:
        return RcpaProvenance("system_supplied", "Source marks the P-code mapping as system-supplied.")
    if text in {"source", "source_supplied", "source_provided"}:
        return RcpaProvenance("source_supplied", "Source provides the P-code directly.")
    if text == "unknown":
        return RcpaProvenance("unknown", "Source marks the P-code mapping provenance as unknown.")
    return RcpaProvenance("unknown", f"Unrecognized source P-code mapping method: {value}.")
