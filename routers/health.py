"""Health check and status endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from redis import Redis
from model.database import get_db
from config import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check endpoint")
async def health_check(db: Session = Depends(get_db)):
    """
    Check application health.

    Verifies database and Redis connectivity.
    """
    services_status = {}

    try:
        # Check database
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        services_status["database"] = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        services_status["database"] = "error"

    try:
        # Check Redis
        redis = Redis.from_url(settings.redis_url)
        redis.ping()
        services_status["cache"] = "ok"
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        services_status["cache"] = "error"

    try:
        # Check Celery
        from celery_app import celery_app
        celery_app.control.inspect().ping()
        services_status["celery"] = "ok"
    except Exception as e:
        logger.warning(f"Celery health check warning: {str(e)}")
        services_status["celery"] = "warning"

    # Determine overall status
    overall_status = "healthy"
    if "error" in services_status.values():
        overall_status = "unhealthy"
    elif "warning" in services_status.values():
        overall_status = "degraded"

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "services": services_status,
        "version": "1.0.0"
    }


@router.get("/ready", summary="Readiness check")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Check if application is ready to serve requests.
    """
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {"status": "not_ready", "error": str(e)}, 503


@router.get("/live", summary="Liveness check")
async def liveness_check():
    """
    Check if application is alive (can respond to requests).
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
