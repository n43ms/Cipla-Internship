from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


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
        self._execute_many(
            """
            insert into plan_events (
                source_file_id, ingestion_run_id, country_id, calendar_month_id, fiscal_year, therapy,
                event_type, event_name, event_name_normalized, central_or_local, brand_name_1, brand_name_2,
                planned_total_hcps, planned_patients, planned_pharmacies, total_planned_cost_usd,
                source_sheet_name, source_row_number
            )
            values (
                :source_file_id, :ingestion_run_id, :country_id, :calendar_month_id, :fiscal_year, :therapy,
                :event_type, :event_name, :event_name_normalized, :central_or_local, :brand_name_1, :brand_name_2,
                :planned_total_hcps, :planned_patients, :planned_pharmacies, :total_planned_cost_usd,
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
        self._execute_many(
            """
            insert into execution_snapshots (
                source_file_id, ingestion_run_id, country_id, calendar_month_id, therapy, event_type,
                event_name, event_name_normalized, planned_hcps, engaged_hcps, raised_request_count,
                snapshot_source, status_source_value, normalized_status, source_sheet_name, source_row_number
            )
            values (
                :source_file_id, :ingestion_run_id, :country_id, :calendar_month_id, :therapy, :event_type,
                :event_name, :event_name_normalized, :planned_hcps, :engaged_hcps, :raised_request_count,
                :snapshot_source, :status_source_value, :normalized_status, :source_sheet_name, :source_row_number
            )
            """,
            ingestion_run_id,
            source_file_id,
            records,
        )

    def insert_execution_requests(
        self, *, ingestion_run_id: str, source_file_id: str, records: list[dict[str, Any]]
    ) -> dict[str, str]:
        request_ids: dict[str, str] = {}
        for record in records:
            params = self._params(ingestion_run_id, source_file_id, record)
            execution_request_id = self.session.execute(
                text(
                    """
                    insert into execution_requests (
                        source_file_id, ingestion_run_id, req_id, request_uid, country_id, calendar_month_id,
                        rep_code, rep_name, venue, intervention_name, intervention_name_normalized,
                        intervention_type, intervention_sub_type, estimated_intervention_local,
                        confirmed_contracted_amount_local, confirmed_vs_estimated_variance_local,
                        actual_total_expense_local, actual_btu_expense_local, actual_btc_expense_local,
                        association_amount_local, currency_code, fx_rate_status, request_approval_status,
                        request_confirmation_status, post_approval_status, post_confirmation_status,
                        current_owner_stage, approval_chain_json, source_row_number
                    )
                    values (
                        :source_file_id, :ingestion_run_id, :req_id, :request_uid, :country_id, :calendar_month_id,
                        :rep_code, :rep_name, :venue, :intervention_name, :intervention_name_normalized,
                        :intervention_type, :intervention_sub_type, :estimated_intervention_local,
                        :confirmed_contracted_amount_local, :confirmed_vs_estimated_variance_local,
                        :actual_total_expense_local, :actual_btu_expense_local, :actual_btc_expense_local,
                        :association_amount_local, :currency_code, :fx_rate_status, :request_approval_status,
                        :request_confirmation_status, :post_approval_status, :post_confirmation_status,
                        :current_owner_stage, cast(:approval_chain_json as json), :source_row_number
                    )
                    on conflict (request_uid) do update
                    set ingestion_run_id = excluded.ingestion_run_id
                    returning id
                    """
                ),
                params,
            ).scalar_one()
            request_ids[str(record["request_key"])] = str(execution_request_id)
        return request_ids

    def insert_request_doctors(self, request_ids: dict[str, str], records: list[dict[str, Any]]) -> None:
        rows = []
        for record in records:
            execution_request_id = request_ids.get(str(record.get("request_key")))
            if not execution_request_id:
                continue
            rows.append({**record, "execution_request_id": execution_request_id})
        if not rows:
            return
        self.session.execute(
            text(
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
            ),
            rows,
        )

    def _execute_many(
        self,
        sql: str,
        ingestion_run_id: str,
        source_file_id: str,
        records: list[dict[str, Any]],
    ) -> None:
        if not records:
            return
        self.session.execute(
            text(sql),
            [self._params(ingestion_run_id, source_file_id, record) for record in records],
        )

    def _params(self, ingestion_run_id: str, source_file_id: str, record: dict[str, Any]) -> dict[str, Any]:
        params = dict(record)
        params["ingestion_run_id"] = ingestion_run_id
        params["source_file_id"] = source_file_id
        params["country_id"] = self.country_id(str(record["country"]))
        params["calendar_month_id"] = self.month_id(record["month_start_date"])
        params["approval_chain_json"] = "{}"
        return params

