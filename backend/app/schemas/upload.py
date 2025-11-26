from pydantic import BaseModel
from typing import Any

from .analytics import AnalyticsSummary, SessionSummary


class AnomalyBreakdown(BaseModel):
    """Breakdown of anomalies detected in uploaded data"""
    total_anomalies: int
    anomaly_percentage: float
    top_anomalies: list[SessionSummary]
    anomaly_reasons_summary: dict[str, int]  # Reason -> count


class UploadAnalyticsResponse(BaseModel):
    ingested_events: int
    summary: AnalyticsSummary
    anomaly_breakdown: AnomalyBreakdown | None = None
    processing_stats: dict[str, Any] | None = None

