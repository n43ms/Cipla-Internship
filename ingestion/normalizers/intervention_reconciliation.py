from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ingestion.normalizers import normalize_event_name


@dataclass(frozen=True)
class DoctorInterventionMatch:
    doctor_record: dict[str, Any]
    request_record: dict[str, Any] | None
    match_method: str
    confidence: float
    reason: str


def reconcile_doctor_interventions(
    doctor_records: list[dict[str, Any]],
    request_records: list[dict[str, Any]],
) -> list[DoctorInterventionMatch]:
    by_request_uid = {
        str(record.get("request_uid") or record.get("req_id")): record
        for record in request_records
        if record.get("request_uid") or record.get("req_id")
    }
    by_normalized_name = {
        _name_key(record): record
        for record in request_records
        if _name_key(record)
    }
    matches: list[DoctorInterventionMatch] = []
    for doctor_record in doctor_records:
        intervention_id = str(doctor_record.get("intervention_id") or "")
        if intervention_id and intervention_id in by_request_uid:
            matches.append(
                DoctorInterventionMatch(
                    doctor_record=doctor_record,
                    request_record=by_request_uid[intervention_id],
                    match_method="intervention_id",
                    confidence=1.0,
                    reason="Doctor-wise intervention ID matched consolidated request ID.",
                )
            )
            continue
        name_key = _name_key(doctor_record)
        request_record = by_normalized_name.get(name_key)
        if request_record:
            matches.append(
                DoctorInterventionMatch(
                    doctor_record=doctor_record,
                    request_record=request_record,
                    match_method="country_month_event_name",
                    confidence=0.8,
                    reason="Doctor-wise row matched consolidated row by country, month, and normalized event name.",
                )
            )
            continue
        matches.append(
            DoctorInterventionMatch(
                doctor_record=doctor_record,
                request_record=None,
                match_method="unmatched",
                confidence=0.0,
                reason="No consolidated request matched the doctor-wise intervention row.",
            )
        )
    return matches


def _name_key(record: dict[str, Any]) -> tuple[object, object, str] | None:
    name = record.get("intervention_name_normalized") or normalize_event_name(
        record.get("intervention_name")
    )
    if not name:
        return None
    return (record.get("country"), record.get("month_start_date"), name)
