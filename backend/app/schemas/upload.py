from pydantic import BaseModel

from .analytics import AnalyticsSummary


class UploadAnalyticsResponse(BaseModel):
    ingested_events: int
    summary: AnalyticsSummary

