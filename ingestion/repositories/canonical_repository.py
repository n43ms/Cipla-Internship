from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from ingestion.normalizers.months import fiscal_year_for

BATCH_SIZE = 5000


class CanonicalRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self._countries: dict[str, str] = {}
        self._months: dict[str, str] = {}

    def country_id(self, country: str) -> str:
        if country not in self._countries:
            value = self.session.execute(
                text("select id from countries where lower(name) = lower(:country) limit 1"),
                {"country": country},
            ).scalar_one()
            self._countries[country] = str(value)
        return self._countries[country]

    def month_id(self, month_start_date: object) -> str:
        month_value = _coerce_month_start(month_start_date)
        key = month_value.isoformat()
        if key not in self._months:
            value = self.session.execute(
                text(
                    """
                    insert into calendar_months (
                        month_start_date,
                        month_label,
                        fiscal_year,
                        fiscal_month_number,
                        calendar_year,
                        calendar_month_number
                    )
                    values (
                        :month_start_date,
                        :month_label,
                        :fiscal_year,
                        :fiscal_month_number,
                        :calendar_year,
                        :calendar_month_number
                    )
                    on conflict (month_start_date) do update
                    set
                        month_label = excluded.month_label,
                        fiscal_year = excluded.fiscal_year,
                        fiscal_month_number = excluded.fiscal_month_number,
                        calendar_year = excluded.calendar_year,
                        calendar_month_number = excluded.calendar_month_number
                    returning id
                    """
                ),
                _month_params(month_value),
            ).scalar_one()
            self._months[key] = str(value)
        return self._months[key]

    def insert_plan_events(
        self, *, ingestion_run_id: str, source_file_id: str, records: list[dict[str, Any]]
    ) -> None:
        self._clear_derived_matches()
        self.session.execute(
            text("delete from plan_events where source_file_id = :source_file_id"),
            {"source_file_id": source_file_id},
        )
        self._execute_many(
            """
            insert into plan_events (
                source_file_id, ingestion_run_id, country_id, calendar_month_id, fiscal_year, therapy,
                event_type, event_name, event_name_normalized, central_or_local, brand_name_1, brand_name_2,
                planned_honorarium_hcps, planned_delegate_hcps, planned_total_hcps, planned_patients,
                planned_pharmacies, honorarium_cost_per_hcp_usd, total_honorarium_cost_usd,
                operational_cost_per_unit_usd, total_operational_cost_usd, total_planned_cost_usd,
                comments, country_comment, ho_finalized,
                source_sheet_name, source_row_number
            )
            values (
                :source_file_id, :ingestion_run_id, :country_id, :calendar_month_id, :fiscal_year, :therapy,
                :event_type, :event_name, :event_name_normalized, :central_or_local, :brand_name_1, :brand_name_2,
                :planned_honorarium_hcps, :planned_delegate_hcps, :planned_total_hcps, :planned_patients,
                :planned_pharmacies, :honorarium_cost_per_hcp_usd, :total_honorarium_cost_usd,
                :operational_cost_per_unit_usd, :total_operational_cost_usd, :total_planned_cost_usd,
                :comments, :country_comment, :ho_finalized,
                :source_sheet_name, :source_row_number
            )
            """,
            ingestion_run_id,
            source_file_id,
            records,
        )

    def insert_execution_snapshots(
        self, *, ingestion_run_id: str, source_file_id: str, records: list[dict[str, Any]]
    ) -> None:
        self._clear_derived_matches()
        self.session.execute(
            text("delete from execution_snapshots where source_file_id = :source_file_id"),
            {"source_file_id": source_file_id},
        )
        self._execute_many(
            """
            insert into execution_snapshots (
                source_file_id, ingestion_run_id, country_id, calendar_month_id, therapy, event_type,
                event_name, event_name_normalized, planned_hcps, engaged_hcps, raised_request_count,
                yp_total_doctors, raised_total_doctors, approved_total_doctors, request_total_doctors,
                event_created_count,
                snapshot_source, status_source_value, normalized_status, source_sheet_name, source_row_number,
                source_derivation_json
            )
            values (
                :source_file_id, :ingestion_run_id, :country_id, :calendar_month_id, :therapy, :event_type,
                :event_name, :event_name_normalized, :planned_hcps, :engaged_hcps, :raised_request_count,
                :yp_total_doctors, :raised_total_doctors, :approved_total_doctors, :request_total_doctors,
                :event_created_count,
                :snapshot_source, :status_source_value, :normalized_status, :source_sheet_name, :source_row_number,
                cast(:source_derivation_json as json)
            )
            """,
            ingestion_run_id,
            source_file_id,
            records,
        )

    def insert_execution_requests(
        self, *, ingestion_run_id: str, source_file_id: str, records: list[dict[str, Any]]
    ) -> dict[str, str]:
        if not records:
            return {}
        self._clear_derived_matches()
        statement = text(
            """
            insert into execution_requests (
                source_file_id, ingestion_run_id, req_id, request_uid, country_id, calendar_month_id,
                rep_code, rep_name, intervention_date, actual_intervention_date, venue,
                intervention_name, intervention_name_normalized,
                intervention_type, intervention_sub_type, estimated_intervention_local,
                confirmed_contracted_amount_local, confirmed_vs_estimated_variance_local,
                actual_total_expense_local, actual_btu_expense_local, actual_btc_expense_local,
                association_amount_local, topic_remarks, association_contract_id, association_deliverables,
                currency_code, fx_rate_to_usd, fx_rate_source, fx_rate_date, fx_rate_status,
                estimated_intervention_usd, confirmed_contracted_amount_usd, actual_total_expense_usd,
                actual_btu_expense_usd, actual_btc_expense_usd, direct_hcp_spend_local,
                overhead_spend_local, total_roi_spend_local, direct_hcp_spend_usd, overhead_spend_usd,
                total_roi_spend_usd, expected_customer_count, attended_customer_count,
                expected_category_raw, attended_category_raw, request_approval_status,
                request_confirmation_status, post_approval_status, post_confirmation_status,
                expense_submitted_date, expense_confirmed_date, current_owner_stage, approval_status,
                confirmation_status, cancellation_reason, city, state, approval_chain_json, source_row_number
            )
            values (
                :source_file_id, :ingestion_run_id, :req_id, :request_uid, :country_id, :calendar_month_id,
                :rep_code, :rep_name, :intervention_date, :actual_intervention_date, :venue,
                :intervention_name, :intervention_name_normalized,
                :intervention_type, :intervention_sub_type, :estimated_intervention_local,
                :confirmed_contracted_amount_local, :confirmed_vs_estimated_variance_local,
                :actual_total_expense_local, :actual_btu_expense_local, :actual_btc_expense_local,
                :association_amount_local, :topic_remarks, :association_contract_id, :association_deliverables,
                :currency_code, :fx_rate_to_usd, :fx_rate_source, :fx_rate_date, :fx_rate_status,
                :estimated_intervention_usd, :confirmed_contracted_amount_usd, :actual_total_expense_usd,
                :actual_btu_expense_usd, :actual_btc_expense_usd, :direct_hcp_spend_local,
                :overhead_spend_local, :total_roi_spend_local, :direct_hcp_spend_usd, :overhead_spend_usd,
                :total_roi_spend_usd, :expected_customer_count, :attended_customer_count,
                :expected_category_raw, :attended_category_raw, :request_approval_status,
                :request_confirmation_status, :post_approval_status, :post_confirmation_status,
                :expense_submitted_date, :expense_confirmed_date, :current_owner_stage, :approval_status,
                :confirmation_status, :cancellation_reason, :city, :state, cast(:approval_chain_json as json),
                :source_row_number
            )
            on conflict (request_uid) do update
            set
                ingestion_run_id = excluded.ingestion_run_id,
                source_file_id = excluded.source_file_id,
                req_id = excluded.req_id,
                country_id = excluded.country_id,
                calendar_month_id = excluded.calendar_month_id,
                rep_code = excluded.rep_code,
                rep_name = excluded.rep_name,
                intervention_date = excluded.intervention_date,
                actual_intervention_date = excluded.actual_intervention_date,
                venue = excluded.venue,
                intervention_name = excluded.intervention_name,
                intervention_name_normalized = excluded.intervention_name_normalized,
                intervention_type = excluded.intervention_type,
                intervention_sub_type = excluded.intervention_sub_type,
                estimated_intervention_local = excluded.estimated_intervention_local,
                confirmed_contracted_amount_local = excluded.confirmed_contracted_amount_local,
                confirmed_vs_estimated_variance_local = excluded.confirmed_vs_estimated_variance_local,
                actual_total_expense_local = excluded.actual_total_expense_local,
                actual_btu_expense_local = excluded.actual_btu_expense_local,
                actual_btc_expense_local = excluded.actual_btc_expense_local,
                association_amount_local = excluded.association_amount_local,
                topic_remarks = excluded.topic_remarks,
                association_contract_id = excluded.association_contract_id,
                association_deliverables = excluded.association_deliverables,
                currency_code = excluded.currency_code,
                fx_rate_to_usd = excluded.fx_rate_to_usd,
                fx_rate_source = excluded.fx_rate_source,
                fx_rate_date = excluded.fx_rate_date,
                fx_rate_status = excluded.fx_rate_status,
                estimated_intervention_usd = excluded.estimated_intervention_usd,
                confirmed_contracted_amount_usd = excluded.confirmed_contracted_amount_usd,
                actual_total_expense_usd = excluded.actual_total_expense_usd,
                actual_btu_expense_usd = excluded.actual_btu_expense_usd,
                actual_btc_expense_usd = excluded.actual_btc_expense_usd,
                direct_hcp_spend_local = excluded.direct_hcp_spend_local,
                overhead_spend_local = excluded.overhead_spend_local,
                total_roi_spend_local = excluded.total_roi_spend_local,
                direct_hcp_spend_usd = excluded.direct_hcp_spend_usd,
                overhead_spend_usd = excluded.overhead_spend_usd,
                total_roi_spend_usd = excluded.total_roi_spend_usd,
                expected_customer_count = excluded.expected_customer_count,
                attended_customer_count = excluded.attended_customer_count,
                expected_category_raw = excluded.expected_category_raw,
                attended_category_raw = excluded.attended_category_raw,
                request_approval_status = excluded.request_approval_status,
                request_confirmation_status = excluded.request_confirmation_status,
                post_approval_status = excluded.post_approval_status,
                post_confirmation_status = excluded.post_confirmation_status,
                expense_submitted_date = excluded.expense_submitted_date,
                expense_confirmed_date = excluded.expense_confirmed_date,
                current_owner_stage = excluded.current_owner_stage,
                approval_status = excluded.approval_status,
                confirmation_status = excluded.confirmation_status,
                cancellation_reason = excluded.cancellation_reason,
                city = excluded.city,
                state = excluded.state,
                approval_chain_json = excluded.approval_chain_json,
                source_row_number = excluded.source_row_number
            """
        )
        params = [self._params(ingestion_run_id, source_file_id, record) for record in records]
        for batch in _chunks(params):
            self.session.execute(statement, batch)
        uids = [str(record["request_uid"]) for record in records]
        request_ids: dict[str, str] = {}
        for batch in [
            uids[index : index + BATCH_SIZE] for index in range(0, len(uids), BATCH_SIZE)
        ]:
            rows = self.session.execute(
                text(
                    "select request_uid, id from execution_requests where request_uid = any(:request_uids)"
                ),
                {"request_uids": batch},
            ).all()
            request_ids.update({str(row[0]): str(row[1]) for row in rows})
        return {
            str(record["request_key"]): request_ids[str(record["request_uid"])]
            for record in records
        }

    def insert_request_doctors(
        self, request_ids: dict[str, str], records: list[dict[str, Any]]
    ) -> None:
        rows = []
        for record in records:
            execution_request_id = request_ids.get(str(record.get("request_key")))
            if not execution_request_id:
                continue
            rows.append({**record, "execution_request_id": execution_request_id})
        if not rows:
            return
        statement = text(
            """
            insert into request_doctors (
                execution_request_id, attendance_type, doctor_name_raw, doctor_class_raw, pcode_raw,
                pcode_normalized, parse_status, source_position
            )
            values (
                :execution_request_id, :attendance_type, :doctor_name_raw, :doctor_class_raw, :pcode_raw,
                :pcode_normalized, :parse_status, :source_position
            )
            on conflict (execution_request_id, attendance_type, source_position) do update
            set
                doctor_name_raw = excluded.doctor_name_raw,
                doctor_class_raw = excluded.doctor_class_raw,
                pcode_raw = excluded.pcode_raw,
                pcode_normalized = excluded.pcode_normalized,
                parse_status = excluded.parse_status
            """
        )
        for batch in _chunks(rows):
            self.session.execute(statement, batch)

    def insert_doctor_engagement_facts(
        self, *, ingestion_run_id: str, source_file_id: str, records: list[dict[str, Any]]
    ) -> None:
        if not records:
            return
        self.session.execute(
            text("delete from doctor_engagement_facts where source_file_id = :source_file_id"),
            {"source_file_id": source_file_id},
        )
        statement = text(
            """
            insert into doctor_engagement_facts (
                source_file_id, ingestion_run_id, country_id, calendar_month_id, region, territory_code,
                fs_hq, request_date, expected_intervention_date, intervention_id, intervention_name,
                intervention_name_normalized, intervention_type, intervention_subtype, pcode_raw,
                pcode_normalized, doctor_segment, doctor_name, estimated_intervention_amount_local,
                btu_expense_local, expense_against_advance_local, btc_expense_local,
                total_actual_intervention_expense_local, fmv_speciality, fmv_tier, fmv_role,
                fmv_amount_local, contract_id, contracted_amount_local, contract_saving_local,
                status, is_sponsorship, sponsorship_class, engagement_class,
                classification_reason, classification_confidence,
                currency_code, fx_rate_to_usd, fx_rate_source, fx_rate_date, fx_rate_status,
                fmv_amount_usd, contracted_amount_usd, contract_saving_usd,
                source_sheet_name, source_row_number, source_row_hash
            )
            values (
                :source_file_id, :ingestion_run_id, :country_id, :calendar_month_id, :region, :territory_code,
                :fs_hq, :request_date, :expected_intervention_date, :intervention_id, :intervention_name,
                :intervention_name_normalized, :intervention_type, :intervention_subtype, :pcode_raw,
                :pcode_normalized, :doctor_segment, :doctor_name, :estimated_intervention_amount_local,
                :btu_expense_local, :expense_against_advance_local, :btc_expense_local,
                :total_actual_intervention_expense_local, :fmv_speciality, :fmv_tier, :fmv_role,
                :fmv_amount_local, :contract_id, :contracted_amount_local, :contract_saving_local,
                :status, :is_sponsorship, :sponsorship_class, :engagement_class,
                :classification_reason, :classification_confidence,
                :currency_code, :fx_rate_to_usd, :fx_rate_source, :fx_rate_date, :fx_rate_status,
                :fmv_amount_usd, :contracted_amount_usd, :contract_saving_usd,
                :source_sheet_name, :source_row_number, :source_row_hash
            )
            on conflict (source_file_id, source_row_hash) do update
            set
                ingestion_run_id = excluded.ingestion_run_id,
                country_id = excluded.country_id,
                calendar_month_id = excluded.calendar_month_id,
                region = excluded.region,
                territory_code = excluded.territory_code,
                fs_hq = excluded.fs_hq,
                request_date = excluded.request_date,
                expected_intervention_date = excluded.expected_intervention_date,
                intervention_id = excluded.intervention_id,
                intervention_name = excluded.intervention_name,
                intervention_name_normalized = excluded.intervention_name_normalized,
                intervention_type = excluded.intervention_type,
                intervention_subtype = excluded.intervention_subtype,
                pcode_raw = excluded.pcode_raw,
                pcode_normalized = excluded.pcode_normalized,
                doctor_segment = excluded.doctor_segment,
                doctor_name = excluded.doctor_name,
                estimated_intervention_amount_local = excluded.estimated_intervention_amount_local,
                btu_expense_local = excluded.btu_expense_local,
                expense_against_advance_local = excluded.expense_against_advance_local,
                btc_expense_local = excluded.btc_expense_local,
                total_actual_intervention_expense_local = excluded.total_actual_intervention_expense_local,
                fmv_speciality = excluded.fmv_speciality,
                fmv_tier = excluded.fmv_tier,
                fmv_role = excluded.fmv_role,
                fmv_amount_local = excluded.fmv_amount_local,
                contract_id = excluded.contract_id,
                contracted_amount_local = excluded.contracted_amount_local,
                contract_saving_local = excluded.contract_saving_local,
                status = excluded.status,
                is_sponsorship = excluded.is_sponsorship,
                sponsorship_class = excluded.sponsorship_class,
                engagement_class = excluded.engagement_class,
                classification_reason = excluded.classification_reason,
                classification_confidence = excluded.classification_confidence,
                currency_code = excluded.currency_code,
                fx_rate_to_usd = excluded.fx_rate_to_usd,
                fx_rate_source = excluded.fx_rate_source,
                fx_rate_date = excluded.fx_rate_date,
                fx_rate_status = excluded.fx_rate_status,
                fmv_amount_usd = excluded.fmv_amount_usd,
                contracted_amount_usd = excluded.contracted_amount_usd,
                contract_saving_usd = excluded.contract_saving_usd,
                source_sheet_name = excluded.source_sheet_name,
                source_row_number = excluded.source_row_number
            """
        )
        for batch in _chunks(
            [self._params(ingestion_run_id, source_file_id, record) for record in records]
        ):
            self.session.execute(statement, batch)
        self._upsert_doctors_from_engagement(records)

    def _upsert_doctors_from_engagement(self, records: list[dict[str, Any]]) -> None:
        rows = []
        for record in records:
            pcode = record.get("pcode_normalized")
            if not pcode:
                continue
            rows.append(
                {
                    "country_id": self.country_id(str(record["country"])),
                    "pcode_normalized": pcode,
                    "latest_doctor_name": record.get("doctor_name"),
                    "doctor_class": record.get("doctor_segment"),
                }
            )
        if not rows:
            return
        statement = text(
            """
            insert into doctors (country_id, pcode_normalized, latest_doctor_name, doctor_class, source_count)
            values (:country_id, :pcode_normalized, :latest_doctor_name, :doctor_class, 1)
            on conflict (country_id, pcode_normalized) do update
            set
                latest_doctor_name = coalesce(excluded.latest_doctor_name, doctors.latest_doctor_name),
                doctor_class = coalesce(excluded.doctor_class, doctors.doctor_class),
                source_count = doctors.source_count + 1,
                updated_at = now()
            """
        )
        for batch in _chunks(rows):
            self.session.execute(statement, batch)

    def insert_msl_doctor_master_records(
        self, *, ingestion_run_id: str, source_file_id: str, records: list[dict[str, Any]]
    ) -> dict[str, int]:
        if not records:
            return {
                "doctor_master_mapping_count": 0,
                "doctor_dimension_upsert_count": 0,
                "engagement_rows_enriched_from_msl": 0,
            }
        self._create_temp_msl_doctor_master_table()
        statement = text(
            """
            insert into tmp_msl_doctor_master_mappings (
                country_id, pcode_raw, pcode_normalized, doctor_name_normalized,
                territory_name, territory_id, doctor_class
            )
            values (
                :country_id, :pcode_raw, :pcode_normalized, :doctor_name_normalized,
                :territory_name, :territory_id, :doctor_class
            )
            """
        )
        rows = [self._params_without_month(ingestion_run_id, source_file_id, record) for record in records]
        for batch in _chunks(rows):
            self.session.execute(statement, batch)
        doctor_count = self._upsert_doctors_from_msl(rows, source_file_id)
        enriched_count = self._enrich_engagements_from_msl()
        return {
            "doctor_master_mapping_count": len(records),
            "doctor_dimension_upsert_count": doctor_count,
            "engagement_rows_enriched_from_msl": enriched_count,
        }

    def _create_temp_msl_doctor_master_table(self) -> None:
        self.session.execute(
            text(
                """
                create temporary table if not exists tmp_msl_doctor_master_mappings (
                    country_id uuid not null,
                    pcode_raw text,
                    pcode_normalized text not null,
                    doctor_name_normalized text not null,
                    territory_name text,
                    territory_id text,
                    doctor_class text
                ) on commit drop
                """
            )
        )
        self.session.execute(text("truncate table tmp_msl_doctor_master_mappings"))

    def _upsert_doctors_from_msl(self, rows: list[dict[str, Any]], source_file_id: str) -> int:
        latest_by_pcode: dict[tuple[str, str], dict[str, Any]] = {}
        for row in rows:
            key = (str(row["country_id"]), str(row["pcode_normalized"]))
            current = latest_by_pcode.setdefault(key, row)
            for field in (
                "doctor_name",
                "doctor_name_normalized",
                "speciality",
                "doctor_class",
                "patch_name",
                "territory_name",
                "territory_id",
                "legacy_code",
            ):
                if not current.get(field) and row.get(field):
                    current[field] = row[field]
        if not latest_by_pcode:
            return 0
        statement = text(
            """
            insert into doctors (
                country_id, pcode_normalized, latest_doctor_name, doctor_name_normalized,
                speciality, doctor_class, patch_name, territory_name, territory_id, legacy_code,
                doctor_master_source_file_id, source_count
            )
            values (
                :country_id, :pcode_normalized, :doctor_name, :doctor_name_normalized,
                :speciality, :doctor_class, :patch_name, :territory_name, :territory_id, :legacy_code,
                :doctor_master_source_file_id, 1
            )
            on conflict (country_id, pcode_normalized) do update
            set
                latest_doctor_name = coalesce(excluded.latest_doctor_name, doctors.latest_doctor_name),
                doctor_name_normalized = coalesce(
                    excluded.doctor_name_normalized,
                    doctors.doctor_name_normalized
                ),
                speciality = coalesce(excluded.speciality, doctors.speciality),
                doctor_class = coalesce(excluded.doctor_class, doctors.doctor_class),
                patch_name = coalesce(excluded.patch_name, doctors.patch_name),
                territory_name = coalesce(excluded.territory_name, doctors.territory_name),
                territory_id = coalesce(excluded.territory_id, doctors.territory_id),
                legacy_code = coalesce(excluded.legacy_code, doctors.legacy_code),
                doctor_master_source_file_id = excluded.doctor_master_source_file_id,
                source_count = doctors.source_count + 1,
                updated_at = now()
            """
        )
        doctor_rows = [
            {**row, "doctor_master_source_file_id": source_file_id}
            for row in latest_by_pcode.values()
        ]
        for batch in _chunks(doctor_rows):
            self.session.execute(statement, batch)
        return len(doctor_rows)

    def _enrich_engagements_from_msl(self) -> int:
        result = self.session.execute(
            text(
                """
                with unique_name_mappings as (
                    select
                        country_id,
                        doctor_name_normalized,
                        min(pcode_raw) filter (where pcode_raw is not null) as pcode_raw,
                        min(pcode_normalized) as pcode_normalized,
                        min(territory_id) filter (where territory_id is not null) as territory_id,
                        min(territory_name) filter (where territory_name is not null) as territory_name,
                        min(doctor_class) filter (where doctor_class is not null) as doctor_class
                    from tmp_msl_doctor_master_mappings
                    group by country_id, doctor_name_normalized
                    having count(distinct pcode_normalized) = 1
                )
                update doctor_engagement_facts def
                set
                    pcode_raw = coalesce(def.pcode_raw, unique_name_mappings.pcode_raw),
                    pcode_normalized = unique_name_mappings.pcode_normalized,
                    territory_code = coalesce(def.territory_code, unique_name_mappings.territory_id),
                    fs_hq = coalesce(def.fs_hq, unique_name_mappings.territory_name),
                    doctor_segment = coalesce(def.doctor_segment, unique_name_mappings.doctor_class)
                from unique_name_mappings
                where def.pcode_normalized is null
                  and def.country_id = unique_name_mappings.country_id
                  and btrim(
                    regexp_replace(lower(def.doctor_name), '[^a-z0-9]+', ' ', 'g')
                  ) = unique_name_mappings.doctor_name_normalized
                """
            )
        )
        return int(result.rowcount or 0)

    def _execute_many(
        self,
        sql: str,
        ingestion_run_id: str,
        source_file_id: str,
        records: list[dict[str, Any]],
    ) -> None:
        if not records:
            return
        statement = text(sql)
        for batch in _chunks(
            [self._params(ingestion_run_id, source_file_id, record) for record in records]
        ):
            self.session.execute(statement, batch)

    def _params(
        self, ingestion_run_id: str, source_file_id: str, record: dict[str, Any]
    ) -> dict[str, Any]:
        params = dict(record)
        params["ingestion_run_id"] = ingestion_run_id
        params["source_file_id"] = source_file_id
        params["country_id"] = self.country_id(str(record["country"]))
        params["calendar_month_id"] = self.month_id(record["month_start_date"])
        params["approval_chain_json"] = json.dumps(record.get("approval_chain_json") or {})
        params["source_derivation_json"] = json.dumps(record.get("source_derivation_json") or {})
        return params

    def _params_without_month(
        self, ingestion_run_id: str, source_file_id: str, record: dict[str, Any]
    ) -> dict[str, Any]:
        params = dict(record)
        params["ingestion_run_id"] = ingestion_run_id
        params["source_file_id"] = source_file_id
        params["country_id"] = self.country_id(str(record["country"]))
        return params

    def _clear_derived_matches(self) -> None:
        self.session.execute(text("delete from event_matches"))


def _chunks(rows: list[dict[str, Any]], size: int = BATCH_SIZE) -> list[list[dict[str, Any]]]:
    return [rows[index : index + size] for index in range(0, len(rows), size)]


def _coerce_month_start(value: object) -> date:
    if isinstance(value, datetime):
        return date(value.year, value.month, 1)
    if isinstance(value, date):
        return date(value.year, value.month, 1)
    return date.fromisoformat(str(value))


def _month_params(month_start_date: date) -> dict[str, object]:
    return {
        "month_start_date": month_start_date,
        "month_label": month_start_date.strftime("%Y-%m"),
        "fiscal_year": fiscal_year_for(month_start_date),
        "fiscal_month_number": ((month_start_date.month - 4) % 12) + 1,
        "calendar_year": month_start_date.year,
        "calendar_month_number": month_start_date.month,
    }
