from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class EventType(str, Enum):
    PAGE_VIEW = "page_view"
    CLICK = "click"
    ACTION = "action"
    SCROLL = "scroll"


class EventPayload(BaseModel):
    session_id: str | None = None
    event_type: EventType
    page: str | None = Field(default=None, max_length=512)
    metadata: dict[str, Any] | None = None
    scroll_depth: float | None = Field(default=None, ge=0, le=100)
    website: str | None = Field(default=None, max_length=512)
    timestamp: datetime

    @model_validator(mode="before")
    def sanitize_nan(cls, values: dict[str, Any]):
        # Convert NaN → None
        for key, val in values.items():
            if isinstance(val, float) and str(val) == "nan":
                values[key] = None
        return values
    @model_validator(mode="after")
    def normalize_metadata(self):
        if self.metadata is None:
            self.metadata = {}
        return self    



class EventIn(EventPayload):
    user_id: str

    @model_validator(mode="after")
    def validate_page(self) -> "EventIn":
        if self.event_type == EventType.PAGE_VIEW and not self.page:
            raise ValueError("page is required for page_view events")
        return self


class EventOut(EventIn):
    id: str

