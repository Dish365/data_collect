"""
API router for v1 endpoints - streamlined analytics API.
"""

from fastapi import APIRouter
from .endpoints import analytics, sync

api_router = APIRouter()

# Streamlined analytics endpoints
api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)

# Sync endpoints
api_router.include_router(
    sync.router,
    prefix="/sync",
    tags=["sync"]
) 