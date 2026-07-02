from __future__ import annotations

from decimal import Decimal
from typing import Literal

from backend.app.schemas.meta import ApiModel, ResponseMeta

FxRateStatus = Literal["official", "provisional", "missing"]


class InterventionMixRow(ApiModel):
    intervention_type: str
    intervention_sub_type: str | None = None
    request_count: int
    executed_count: int
    executed_request_count: int = 0
    matched_request_count: int = 0
    executed_snapshot_count: int = 0
    action_due_count: int = 0
    action_due_request_count: int = 0
    action_due_snapshot_count: int = 0
    matched_without_execution_count: int = 0
    approved_count: int
    report_pending_count: int
    confirmed_contracted_amount: Decimal | None = None
    direct_hcp_btu_spend: Decimal | None = None
    overhead_btc_spend: Decimal | None = None
    total_actual_spend: Decimal | None = None
    fx_rate_status: FxRateStatus | str


class InterventionMixResponse(ApiModel):
    meta: ResponseMeta
    rows: list[InterventionMixRow]
