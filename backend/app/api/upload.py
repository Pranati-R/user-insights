from fastapi import APIRouter, Depends, File, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo import get_database
from app.services import auth_service
from app.services.analytics_service import AnalyticsService
from app.utils.responses import success

router = APIRouter(tags=["upload"])


@router.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(auth_service.get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = AnalyticsService(db)
    result = await service.process_upload(str(current_user["_id"]), file)
    return success(result.model_dump())

