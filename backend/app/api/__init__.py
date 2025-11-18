from app.api.auth import router as auth_router
from app.api.events import router as events_router
from app.api.analytics import router as analytics_router
from app.api.upload import router as upload_router

__all__ = ["auth_router", "events_router", "analytics_router", "upload_router"]



