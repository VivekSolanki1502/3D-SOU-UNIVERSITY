from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.redis import get_redis_client
from app.core.config import settings
from app.db.session import get_db

router = APIRouter()


@router.get("/health", summary="Health check endpoint")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint returning system status.
    """
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

    redis_client = await get_redis_client()
    redis_status = "connected" if redis_client else ("unavailable" if settings.REDIS_ENABLED else "disabled")
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected",
        "redis": redis_status,
    }
