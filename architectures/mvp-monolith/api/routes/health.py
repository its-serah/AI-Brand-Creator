"""
Health check API routes
"""

from fastapi import APIRouter, HTTPException
import logging
from datetime import datetime

from ..models.base import HealthResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint"""
    try:
        services_status = {
            "api": "healthy",
            "database": "not_checked",  # Would check Neo4j connection
            "storage": "not_checked",   # Would check S3 connection
            "ai_models": "not_checked"  # Would check model availability
        }
        
        return HealthResponse(
            status="healthy",
            version="1.0.0", 
            timestamp=datetime.now(),
            services=services_status
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@router.get("/ready", response_model=HealthResponse)
async def readiness_check():
    """Readiness check for Kubernetes"""
    try:
        # In a real implementation, you would check:
        # - Database connectivity
        # - AI model loading status
        # - External service availability
        
        services_status = {
            "api": "ready",
            "database": "ready",
            "storage": "ready", 
            "ai_models": "ready"
        }
        
        return HealthResponse(
            status="ready",
            version="1.0.0",
            timestamp=datetime.now(),
            services=services_status
        )
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/live", response_model=HealthResponse)
async def liveness_check():
    """Liveness check for Kubernetes"""
    try:
        return HealthResponse(
            status="alive",
            version="1.0.0",
            timestamp=datetime.now(),
            services={"api": "alive"}
        )
        
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not alive")
