from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Iterable

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import get_settings
from app.services.metrics import compute_metrics
from app.services.ml_service import score_session

settings = get_settings()


def group_events_into_sessions(events: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    sessions: list[dict[str, Any]] = []
    idle_threshold = timedelta(minutes=settings.session_idle_minutes)

    # Bucket events per user for deterministic grouping
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        buckets[event["user_id"]].append(event)

    for user_id, user_events in buckets.items():
        ordered = sorted(user_events, key=lambda e: e["timestamp"])
        session_events: list[dict[str, Any]] = []
        session_id = ObjectId()

        prev_ts: datetime | None = None
        for event in ordered:
            timestamp: datetime = event["timestamp"]
            if not session_events:
                session_events.append(event)
                prev_ts = timestamp
                continue

            assert prev_ts is not None  # mypy appeasement
            if timestamp - prev_ts > idle_threshold:
                sessions.append(build_session(session_id, user_id, session_events))
                session_id = ObjectId()
                session_events = []

            session_events.append(event)
            prev_ts = timestamp

        if session_events:
            sessions.append(build_session(session_id, user_id, session_events))

    return sessions


def build_session(session_id: ObjectId, user_id: str, events: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = compute_metrics(events)
    start_ts = min(event["timestamp"] for event in events)
    end_ts = max(event["timestamp"] for event in events)
    anomaly = score_session(metrics)

    # Convert NumPy types to Python native types for MongoDB
    def convert_numpy_types(obj):
        """Recursively convert numpy types to Python native types"""
        import numpy as np
        if isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(item) for item in obj]
        return obj

    return {
        "_id": session_id,
        "session_id": str(session_id),
        "user_id": user_id,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "metrics": metrics.model_dump(),
        "anomaly_score": float(anomaly["score"]),
        "raw_anomaly_score": float(anomaly.get("raw_score", 0)),
        "is_anomalous": bool(anomaly["is_anomalous"]),
        "anomaly_reasons": list(anomaly.get("anomaly_reasons", [])),
        "feature_snapshot": convert_numpy_types(anomaly["features"]),
        "feature_contributions": convert_numpy_types(anomaly.get("feature_contributions", {})),
        "event_ids": [event["_id"] for event in events if "_id" in event],
    }


async def rebuild_sessions_for_user(db: AsyncIOMotorDatabase, user_id: str) -> list[dict[str, Any]]:
    events_cursor = (
        db[settings.events_collection]
        .find({"user_id": user_id})
        .sort("timestamp", 1)
    )
    events = await events_cursor.to_list(length=None)
    sessions = group_events_into_sessions(events)

    sessions_collection = db[settings.sessions_collection]
    if not sessions:
        await sessions_collection.delete_many({"user_id": user_id})
        return []

    await sessions_collection.delete_many({"user_id": user_id})
    await sessions_collection.insert_many(sessions)
    return sessions

