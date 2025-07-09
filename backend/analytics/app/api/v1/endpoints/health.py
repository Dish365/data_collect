"""
Health check endpoints for the API.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict
from core.database import get_db
from core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.
    
    Returns:
        Dictionary with health status
    """
    return {
        "status": "healthy",
        "version": settings.VERSION
    }

@router.get("/health/db")
async def database_health_check(db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Database health check endpoint.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with database health status
    """
    try:
        # Try to execute a simple query on FastAPI database
        db.execute("SELECT 1")
        fastapi_db_status = "connected"
    except Exception as e:
        fastapi_db_status = f"disconnected: {str(e)}"
    
    # Also check Django database
    try:
        from app.utils.shared import AnalyticsUtils
        conn = AnalyticsUtils.get_django_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        conn.close()
        django_db_status = f"connected ({table_count} tables)"
    except Exception as e:
        django_db_status = f"disconnected: {str(e)}"
    
    overall_status = "healthy" if "connected" in fastapi_db_status and "connected" in django_db_status else "unhealthy"
    
    return {
        "status": overall_status,
        "fastapi_database": fastapi_db_status,
        "django_database": django_db_status
    } 