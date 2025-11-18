from __future__ import annotations

import json
from datetime import datetime
from io import StringIO
from typing import Any
from uuid import uuid4

import pandas as pd
from fastapi import HTTPException, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import get_settings
from app.schemas.analytics import AnalyticsSummary, SessionMetrics, SessionSummary
from app.schemas.events import EventIn, EventPayload
from app.schemas.upload import UploadAnalyticsResponse
from app.services.sessionizer import rebuild_sessions_for_user

settings = get_settings()

def is_nan(v):
    return isinstance(v, float) and str(v) == "nan"

class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.events = db[settings.events_collection]
        self.sessions = db[settings.sessions_collection]

    async def record_event(self, event: EventIn) -> dict[str, Any]:
        doc = event.model_dump()
        doc.setdefault("session_id", str(uuid4()))
        doc["timestamp"] = event.timestamp
        result = await self.events.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def summary(self, user_id: str) -> AnalyticsSummary:
        total_events = await self.events.count_documents({"user_id": user_id})
        total_sessions = await self.sessions.count_documents({"user_id": user_id})
        anomalies = await self.sessions.count_documents({"user_id": user_id, "is_anomalous": True})
        last_event = await self.events.find({"user_id": user_id}).sort("timestamp", -1).limit(1).to_list(1)

        pipeline = [
            {"$match": {"user_id": user_id, "page": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": "$page", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5},
        ]
        top_pages_raw = await self.events.aggregate(pipeline).to_list(length=5)
        top_pages = [{"page": doc["_id"], "count": doc["count"]} for doc in top_pages_raw]

        anomaly_rate = (anomalies / total_sessions) * 100 if total_sessions else 0.0
        last_event_at = last_event[0]["timestamp"] if last_event else None

        return AnalyticsSummary(
            total_events=total_events,
            total_sessions=total_sessions,
            anomaly_rate=anomaly_rate,
            last_event_at=last_event_at,
            top_pages=top_pages,
        )

    async def list_events(self, user_id: str, limit: int = 200) -> list[dict[str, Any]]:
        cursor = (
            self.events.find({"user_id": user_id})
            .sort("timestamp", -1)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc["id"] = str(doc["_id"])
            doc["_id"] = str(doc["_id"])
        return docs

    async def list_sessions(self, user_id: str, limit: int = 50) -> list[SessionSummary]:
        docs = (
            await self.sessions.find({"user_id": user_id})
            .sort("start_ts", -1)
            .limit(limit)
            .to_list(length=limit)
        )
        summaries = []
        for doc in docs:
            summaries.append(
                SessionSummary(
                    session_id=doc["session_id"],
                    user_id=doc["user_id"],
                    start_ts=doc["start_ts"],
                    end_ts=doc["end_ts"],
                    metrics=SessionMetrics(**doc["metrics"]),
                    anomaly_score=doc.get("anomaly_score"),
                    is_anomalous=doc.get("is_anomalous"),
                )
            )
        return summaries

    async def list_anomalies(self, user_id: str, limit: int = 50) -> list[SessionSummary]:
        docs = (
            await self.sessions.find({"user_id": user_id, "is_anomalous": True})
            .sort("end_ts", -1)
            .limit(limit)
            .to_list(length=limit)
        )
        return [
            SessionSummary(
                session_id=doc["session_id"],
                user_id=doc["user_id"],
                start_ts=doc["start_ts"],
                end_ts=doc["end_ts"],
                metrics=SessionMetrics(**doc["metrics"]),
                anomaly_score=doc.get("anomaly_score"),
                is_anomalous=doc.get("is_anomalous"),
            )
            for doc in docs
        ]

    async def process_upload(self, user_id: str, file: UploadFile) -> UploadAnalyticsResponse:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
        print("contents")
        events = self._parse_file(contents, file.filename or "")
        inserted = 0
       
        for raw_event in events:
          
            raw_type = raw_event.get("event_type")
            if is_nan(raw_type) or raw_type in (None, ""):
                raw_type = raw_event.get("type")
            if raw_type:
                raw_type = str(raw_type).strip().lower()
            else:
                raw_type = None

            # If still missing, infer automatically
            if raw_type is None:
                if raw_event.get("scroll_depth") not in (None, float("nan")):
                    raw_type = "scroll"
                elif raw_event.get("action"):
                    raw_type = "action"
                elif raw_event.get("page"):
                    raw_type = "page_view"
                else:
                    raw_type = "action"
            raw_metadata = raw_event.get("metadata")
            if raw_metadata is None or isinstance(raw_metadata, float):
                raw_metadata = {}
                    
            payload = EventPayload(
                session_id=raw_event.get("session_id"),
                event_type=raw_type,
                page=raw_event.get("page"),
                metadata=raw_metadata,
                scroll_depth=raw_event.get("scroll_depth"),
                website=raw_event.get("website"),
                timestamp=self._parse_timestamp(raw_event.get("timestamp")),
            )
            print(payload)
            await self.record_event(EventIn(user_id=user_id, **payload.model_dump()))
            inserted += 1

        await rebuild_sessions_for_user(self.db, user_id)
        summary = await self.summary(user_id)

        return UploadAnalyticsResponse(ingested_events=inserted, summary=summary)

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))

    @staticmethod
    def _parse_file(contents: bytes, filename: str) -> list[dict[str, Any]]:
        if filename.lower().endswith(".json"):
            data = json.loads(contents.decode("utf-8"))
            if isinstance(data, dict):
                data = data.get("events", [])
            if not isinstance(data, list):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON structure")
            return data

        if filename.lower().endswith(".csv"):
            df = pd.read_csv(StringIO(contents.decode("utf-8")))
            return df.to_dict(orient="records")

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

