"""Shared normalization entry points for ingestion.

Concrete normalizers are implemented in later phases. This module defines the
package boundary and stable import path for tests and loaders.
"""

__all__ = [
    "currencies",
    "events",
    "months",
    "pcodes",
    "statuses",
    "workflow_status",
]
