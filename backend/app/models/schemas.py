from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class EventType(str, Enum):
    PAGE_VIEW = "page_view"
    CLICK = "click"
    ACTION = "action"


class EventIn(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=128)
    type: EventType
    timestamp: datetime
    page: str | None = Field(default=None, max_length=256)
    action: str | None = Field(default=None, max_length=256)
    session_hint: str | None = Field(default=None, max_length=128)
    metadata: dict[str, Any] | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> "EventIn":
        if self.type == EventType.PAGE_VIEW and not self.page:
            raise ValueError("page is required for page_view events")
        if self.type == EventType.ACTION and not self.action:
            raise ValueError("action is required for action events")
        return self


class EventOut(EventIn):
    id: str


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
    explanations: dict[str, float] | None = None


