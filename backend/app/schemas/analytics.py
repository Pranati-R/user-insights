from datetime import datetime
from typing import Any

from pydantic import BaseModel


class SessionMetrics(BaseModel):
    duration_seconds: float
    event_count: int
    click_rate: float
    unique_pages: int
    action_diversity: int
    avg_inter_event_seconds: float
    dwell_estimate_seconds: float


class SessionSummary(BaseModel):
    session_id: str
    user_id: str
    start_ts: datetime
    end_ts: datetime
    metrics: SessionMetrics
    anomaly_score: float | None = None
    is_anomalous: bool | None = None


class SessionFilter(BaseModel):
    user_id: str | None = None
    start: datetime | None = None
    end: datetime | None = None
    anomalous_only: bool | None = None


class AnomalyResponse(BaseModel):
    session_id: str
    score: float
    is_anomalous: bool
    explanations: dict[str, Any] | None = None


class AnalyticsSummary(BaseModel):
    total_events: int
    total_sessions: int
    anomaly_rate: float
    last_event_at: datetime | None
    top_pages: list[dict[str, Any]]

