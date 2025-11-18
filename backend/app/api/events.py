from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import get_settings
from app.db.mongo import get_database
from app.schemas.events import EventIn, EventPayload
from app.services import auth_service
from app.services.analytics_service import AnalyticsService
from app.services.sessionizer import rebuild_sessions_for_user
from app.utils.responses import success

router = APIRouter(tags=["events"])
settings = get_settings()
TRACKING_SCRIPT_PATH = Path(__file__).resolve().parent.parent / "static" / "track.js"


@router.get("/track.js")
async def tracking_script() -> FileResponse:
    if not TRACKING_SCRIPT_PATH.exists():
        raise HTTPException(status_code=500, detail="Tracking script missing on server")
    return FileResponse(TRACKING_SCRIPT_PATH, media_type="application/javascript")


@router.post("/collect")
async def collect_event(
    payload: EventPayload,
    uid: str = Query(..., description="User ID that owns the site"),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    try:
        user_obj_id = ObjectId(uid)
    except InvalidId as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") from exc

    user = await db[settings.users_collection].find_one({"_id": user_obj_id})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    session_id = payload.session_id or str(uuid4())
    event_data = payload.model_dump()
    event_data["session_id"] = session_id
    event = EventIn(user_id=str(user_obj_id), **event_data)

    service = AnalyticsService(db)
    await service.record_event(event)
    await rebuild_sessions_for_user(db, str(user_obj_id))

    return success({"session_id": session_id})


@router.get("/events")
async def list_events(
    current_user: dict = Depends(auth_service.get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = AnalyticsService(db)
    events = await service.list_events(str(current_user["_id"]))
    return success({"events": events})

