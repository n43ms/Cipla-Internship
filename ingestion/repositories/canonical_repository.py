from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


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
        key = str(month_start_date)
        if key not in self._months:
            value = self.session.execute(
                text("select id from calendar_months where month_start_date = :month_start_date limit 1"),
                {"month_start_date": month_start_date},
            ).scalar_one()
            self._months[key] = str(value)
        return self._months[key]

    def insert_plan_events(self, *, ingestion_run_id: str, source_file_id: str, records: list[dict[str, Any]]) -> None:
        self._clear_derived_matches()
        self.session.execute(text("delete from plan_events where source_file_id = :source_file_id"), {"source_file_id": source_file_id})
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
        for batch in [uids[index : index + BATCH_SIZE] for index in range(0, len(uids), BATCH_SIZE)]:
            rows = self.session.execute(
                text("select request_uid, id from execution_requests where request_uid = any(:request_uids)"),
                {"request_uids": batch},
            ).all()
            request_ids.update({str(row[0]): str(row[1]) for row in rows})
        return {str(record["request_key"]): request_ids[str(record["request_uid"])] for record in records}

    def insert_request_doctors(self, request_ids: dict[str, str], records: list[dict[str, Any]]) -> None:
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
        for batch in _chunks([self._params(ingestion_run_id, source_file_id, record) for record in records]):
            self.session.execute(statement, batch)

    def _params(self, ingestion_run_id: str, source_file_id: str, record: dict[str, Any]) -> dict[str, Any]:
        params = dict(record)
        params["ingestion_run_id"] = ingestion_run_id
        params["source_file_id"] = source_file_id
        params["country_id"] = self.country_id(str(record["country"]))
        params["calendar_month_id"] = self.month_id(record["month_start_date"])
        params["approval_chain_json"] = json.dumps(record.get("approval_chain_json") or {})
        params["source_derivation_json"] = json.dumps(record.get("source_derivation_json") or {})
        return params

    def _clear_derived_matches(self) -> None:
        self.session.execute(text("delete from event_matches"))


def _chunks(rows: list[dict[str, Any]], size: int = BATCH_SIZE) -> list[list[dict[str, Any]]]:
    return [rows[index : index + size] for index in range(0, len(rows), size)]
