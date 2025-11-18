from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analytics_router, auth_router, events_router, upload_router
from app.core.config import get_settings
from app.utils.responses import success

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return success({"status": "ok"})


app.include_router(auth_router)
app.include_router(events_router)
app.include_router(analytics_router)
app.include_router(upload_router)


