from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo import get_database
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserPublic
from app.services import auth_service
from app.utils.responses import success

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
async def signup(payload: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    user = await auth_service.register_user(db, payload)
    token = auth_service.create_access_token({"sub": user.id, "email": user.email})
    return success(TokenResponse(access_token=token, user=user).model_dump())


@router.post("/login")
async def login(payload: UserLogin, db: AsyncIOMotorDatabase = Depends(get_database)):
    token = await auth_service.authenticate_user(db, payload)
    return success(token.model_dump())


@router.get("/me")
async def me(current_user: dict = Depends(auth_service.get_current_user)):
    public_user = UserPublic(
        id=str(current_user["_id"]),
        email=current_user["email"],
        name=current_user["name"],
        created_at=current_user["created_at"],
    )
    return success(public_user.model_dump())

