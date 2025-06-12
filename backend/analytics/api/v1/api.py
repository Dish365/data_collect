"""
Main API router for version 1 endpoints.
"""

from fastapi import APIRouter
from .endpoints import descriptive, inferential, qualitative, auto_detect

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(descriptive.router, prefix="/descriptive", tags=["descriptive"])
api_router.include_router(inferential.router, prefix="/inferential", tags=["inferential"])
api_router.include_router(qualitative.router, prefix="/qualitative", tags=["qualitative"])
api_router.include_router(auto_detect.router, prefix="/auto-detect", tags=["auto-detect"]) 