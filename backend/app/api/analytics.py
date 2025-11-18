from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import get_settings
from app.db.mongo import get_database
from app.schemas.analytics import AnomalyResponse, SessionMetrics
from app.services import auth_service
from app.services.analytics_service import AnalyticsService
from app.services.ml_service import score_session
from app.utils.responses import success

router = APIRouter(prefix="/analytics", tags=["analytics"])
settings = get_settings()


@router.get("/summary")
async def analytics_summary(
    current_user: dict = Depends(auth_service.get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = AnalyticsService(db)
    summary = await service.summary(str(current_user["_id"]))
    return success(summary.model_dump())


@router.get("/sessions")
async def analytics_sessions(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: dict = Depends(auth_service.get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = AnalyticsService(db)
    sessions = await service.list_sessions(str(current_user["_id"]), limit=limit)
    return success({"sessions": [session.model_dump() for session in sessions]})


@router.get("/anomalies")
async def analytics_anomalies(
    limit: int = Query(default=25, ge=1, le=100),
    current_user: dict = Depends(auth_service.get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = AnalyticsService(db)
    sessions = await service.list_anomalies(str(current_user["_id"]), limit=limit)
    return success({"anomalies": [session.model_dump() for session in sessions]})


@router.get("/sessions/{session_id}/anomaly")
async def session_anomaly(
    session_id: str,
    current_user: dict = Depends(auth_service.get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    doc = await db[settings.sessions_collection].find_one(
        {"session_id": session_id, "user_id": str(current_user["_id"])}
    )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    result = score_session(SessionMetrics(**doc["metrics"]))
    payload = AnomalyResponse(
        session_id=session_id,
        score=result["score"],
        is_anomalous=result["is_anomalous"],
        explanations={"feature_vector": result["features"]},
    )
    return success(payload.model_dump())

