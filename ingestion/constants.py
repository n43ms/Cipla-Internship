from enum import StrEnum


class SourceType(StrEnum):
    PLANNER = "planner"
    EXECUTION_SNAPSHOT = "execution_snapshot"
    CONSOLIDATION = "consolidation"
    RCPA = "rcpa"


class CountryCode(StrEnum):
    NEPAL = "NP"
    SRI_LANKA = "LK"
    MYANMAR = "MM"
    OMAN = "OM"
    UAE = "AE"
    MALAYSIA = "MY"


class SnapshotSource(StrEnum):
    MONTHLY_PLANNER = "monthly_planner"
    DERIVED_FROM_CONSOLIDATION = "derived_from_consolidation"


class MatchStatus(StrEnum):
    MATCHED = "matched"
    WEAK_MATCH = "weak_match"
    UNMATCHED_PLAN = "unmatched_plan"
    UNMATCHED_SNAPSHOT = "unmatched_snapshot"
    UNMATCHED_REQUEST = "unmatched_request"
    IGNORED = "ignored"


class RoiSegment(StrEnum):
    HIGH_VALUE_ENGAGED = "high_value_engaged"
    HIGH_VALUE_UNENGAGED = "high_value_unengaged"
    LOW_RX_HIGH_SPEND = "low_rx_high_spend"
    INSUFFICIENT_DATA = "insufficient_data"


OFFICIAL_LKR_PER_USD = 310.0
