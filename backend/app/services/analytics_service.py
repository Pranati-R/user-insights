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
from app.schemas.upload import UploadAnalyticsResponse, AnomalyBreakdown
from app.services.sessionizer import rebuild_sessions_for_user
from app.services.intelligent_parser import IntelligentLogParser
from collections import Counter
from app.services.sessionizer import group_events_into_sessions
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

    # async def process_upload(self, user_id: str, file: UploadFile) -> UploadAnalyticsResponse:
    #     contents = await file.read()
    #     if not contents:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
        
    #     # Use intelligent parser to handle multiple formats
    #     parser = IntelligentLogParser()
    #     raw_events = parser.parse_file(contents, file.filename or "")
        
    #     if not raw_events:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="No valid events found in file"
    #         )
        
    #     inserted = 0
    #     failed = 0
        
    #     for raw_event in raw_events:
    #         try:
    #             # Use intelligent normalization
    #             normalized = parser.normalize_log_entry(raw_event)
                
    #             # Extract and validate required fields
    #             event_type = normalized.get("event_type")
    #             if not event_type:
    #                 # Infer from other fields
    #                 if normalized.get("scroll_depth") is not None:
    #                     event_type = "scroll"
    #                 elif normalized.get("page"):
    #                     event_type = "page_view"
    #                 else:
    #                     event_type = "action"
                
    #             timestamp = normalized.get("timestamp")
    #             if not timestamp:
    #                 # Use current time as fallback
    #                 timestamp = datetime.utcnow()
                
    #             # Build event payload
    #             payload = EventPayload(
    #                 session_id=normalized.get("session_id"),
    #                 event_type=event_type,
    #                 page=normalized.get("page"),
    #                 metadata=normalized.get("metadata", {}),
    #                 scroll_depth=normalized.get("scroll_depth"),
    #                 website=normalized.get("website"),
    #                 timestamp=timestamp,
    #             )
                
    #             # Temporarily store events instead of recording permanently
    #             await self.record_event(EventIn(user_id=user_id, **payload.model_dump()))
    #             inserted += 1
                
    #         except Exception as e:
    #             failed += 1
    #             print(f"Failed to process event: {e}")
    #             continue

    #     if inserted == 0:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail=f"Failed to process any events. {failed} events had errors."
    #         )

    #     await rebuild_sessions_for_user(self.db, user_id)
    #     summary = await self.summary(user_id)
        
    #     # Get anomaly breakdown
    #     anomaly_breakdown = await self._get_anomaly_breakdown(user_id)
        
    #     # Processing stats
    #     processing_stats = {
    #         "total_events_in_file": len(raw_events),
    #         "successfully_inserted": inserted,
    #         "failed_events": failed,
    #         "success_rate": (inserted / len(raw_events)) * 100 if raw_events else 0,
    #     }

    #     return UploadAnalyticsResponse(
    #         ingested_events=inserted,
    #         summary=summary,
    #         anomaly_breakdown=anomaly_breakdown,
    #         processing_stats=processing_stats
    #     )
    async def process_upload(self, user_id: str, file: UploadFile) -> UploadAnalyticsResponse:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")

        parser = IntelligentLogParser()
        raw_events = parser.parse_file(contents, file.filename or "")

        if not raw_events:
            raise HTTPException(status_code=400, detail="No valid events found")

        parsed_events = []
        failed = 0

        for raw in raw_events:
            try:
                normalized = parser.normalize_log_entry(raw)

                # -------------------------------------------------------------------
                # DETERMINE event_type intelligently
                # -------------------------------------------------------------------
                event_type = normalized.get("event_type")
                if not event_type:
                    if normalized.get("scroll_depth") is not None:
                        event_type = "scroll"
                    elif normalized.get("page"):
                        event_type = "page_view"
                    else:
                        event_type = "action"

                timestamp = normalized.get("timestamp") or datetime.utcnow()

                payload = EventPayload(
                    session_id=normalized.get("session_id"),
                    event_type=event_type,
                    page=normalized.get("page"),
                    metadata=normalized.get("metadata", {}),
                    scroll_depth=normalized.get("scroll_depth"),
                    website=normalized.get("website"),
                    timestamp=timestamp,
                )

                # -------------------------------------------------------------------
                # ❗ DO NOT INSERT INTO DB — USE IN MEMORY
                # -------------------------------------------------------------------
                evt = payload.model_dump()
                evt["user_id"] = user_id
                parsed_events.append(evt)

            except Exception as e:
                failed += 1
                print("Failed event:", raw, "\nError:", e)
                continue

        if not parsed_events:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process any events. ({failed} events invalid)"
            )

        # -------------------------------------------------------------------
        # 👇 MEMORY-ONLY SESSIONIZER (NO DATABASE)
        # -------------------------------------------------------------------
        sessions = group_events_into_sessions(parsed_events)

        # -------------------------------------------------------------------
        # BUILD ANOMALY BREAKDOWN
        # -------------------------------------------------------------------
        total_sessions = len(sessions)
        anomalies = [s for s in sessions if s["is_anomalous"]]
        anomaly_percentage = (len(anomalies) / total_sessions * 100) if total_sessions else 0

        reason_counts = Counter(
            reason
            for sess in anomalies
            for reason in sess.get("anomaly_reasons", [])
        )

        top_anomalies = anomalies[:5]

        anomaly_breakdown = AnomalyBreakdown(
            total_anomalies=len(anomalies),
            anomaly_percentage=anomaly_percentage,
            top_anomalies=[
                SessionSummary(
                    session_id=s["session_id"],
                    user_id=s["user_id"],
                    start_ts=s["start_ts"],
                    end_ts=s["end_ts"],
                    metrics=SessionMetrics(**s["metrics"]),
                    anomaly_score=s["anomaly_score"],
                    is_anomalous=s["is_anomalous"],
                )
                for s in top_anomalies
            ],
            anomaly_reasons_summary=dict(reason_counts),
        )

        # -------------------------------------------------------------------
        # BUILD PROCESSING STATS
        # -------------------------------------------------------------------
        processing_stats = {
            "total_events_in_file": len(raw_events),
            "successfully_parsed": len(parsed_events),
            "failed_events": failed,
            "success_rate": (len(parsed_events) / len(raw_events) * 100),
            "sessions_detected": total_sessions,
        }

        summary = AnalyticsSummary(
            total_events=len(parsed_events),
            total_sessions=total_sessions,
            anomaly_rate=anomaly_percentage,
            last_event_at=max(e["timestamp"] for e in parsed_events),
            top_pages=[],
        )

        return UploadAnalyticsResponse(
            ingested_events=len(parsed_events),
            summary=summary,
            anomaly_breakdown=anomaly_breakdown,
            processing_stats=processing_stats,
            sessions=[
                SessionSummary(
                    session_id=s["session_id"],
                    user_id=s["user_id"],
                    start_ts=s["start_ts"],
                    end_ts=s["end_ts"],
                    metrics=SessionMetrics(**s["metrics"]),
                    anomaly_score=s["anomaly_score"],
                    is_anomalous=s["is_anomalous"],
                )
                for s in sessions
            ]
        )

    async def _get_anomaly_breakdown(self, user_id: str) -> AnomalyBreakdown:
        """Get detailed anomaly breakdown for uploaded data"""
        # Get all anomalous sessions
        anomalous_sessions = await self.sessions.find(
            {"user_id": user_id, "is_anomalous": True}
        ).sort("anomaly_score", -1).to_list(length=None)
        
        total_sessions = await self.sessions.count_documents({"user_id": user_id})
        total_anomalies = len(anomalous_sessions)
        anomaly_percentage = (total_anomalies / total_sessions * 100) if total_sessions > 0 else 0
        
        # Collect all anomaly reasons
        all_reasons = []
        for session in anomalous_sessions:
            reasons = session.get("anomaly_reasons", [])
            all_reasons.extend(reasons)
        
        # Count reason occurrences
        reason_counts = dict(Counter(all_reasons))
        
        # Get top 5 anomalies
        top_anomalies = []
        for doc in anomalous_sessions[:5]:
            top_anomalies.append(
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
        
        return AnomalyBreakdown(
            total_anomalies=total_anomalies,
            anomaly_percentage=anomaly_percentage,
            top_anomalies=top_anomalies,
            anomaly_reasons_summary=reason_counts
        )
