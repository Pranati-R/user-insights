from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorDatabase
from passlib.context import CryptContext

from app.core.config import get_settings
from app.db.mongo import get_database
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserPublic

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.jwt_exp_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def serialize_user(doc: dict[str, Any]) -> UserPublic:
    return UserPublic(
        id=str(doc["_id"]),
        email=doc["email"],
        name=doc["name"],
        created_at=doc["created_at"],
    )


async def register_user(db: AsyncIOMotorDatabase, payload: UserCreate) -> UserPublic:
    users = db[settings.users_collection]
    existing = await users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    doc = {
        "email": payload.email.lower(),
        "name": payload.name,
        "password": hash_password(payload.password),
        "created_at": datetime.now(timezone.utc),
    }
    result = await users.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_user(doc)


async def authenticate_user(db: AsyncIOMotorDatabase, payload: UserLogin) -> TokenResponse:
    users = db[settings.users_collection]
    doc = await users.find_one({"email": payload.email.lower()})
    if not doc or not verify_password(payload.password, doc["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": str(doc["_id"]), "email": doc["email"]})
    return TokenResponse(access_token=token, user=serialize_user(doc))


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, Any]:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    users = db[settings.users_collection]
    user = await users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

