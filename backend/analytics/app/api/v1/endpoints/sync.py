"""
Data synchronization endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from ....core.database import get_db
from ....sync.manager import SyncManager
from ....sync.conflict_resolver import ConflictResolver

router = APIRouter()

@router.post("/sync/start")
async def start_sync(
    source: str,
    target: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start a data synchronization process.
    
    Args:
        source: Source system identifier
        target: Target system identifier
        db: Database session
        
    Returns:
        Dictionary with sync status
    """
    try:
        sync_manager = SyncManager(db)
        sync_id = await sync_manager.start_sync(source, target)
        return {
            "status": "started",
            "sync_id": sync_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start sync: {str(e)}"
        )

@router.get("/sync/{sync_id}/status")
async def get_sync_status(
    sync_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the status of a synchronization process.
    
    Args:
        sync_id: Synchronization process identifier
        db: Database session
        
    Returns:
        Dictionary with sync status details
    """
    try:
        sync_manager = SyncManager(db)
        status = await sync_manager.get_status(sync_id)
        return status
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Sync process not found: {str(e)}"
        )

@router.post("/sync/{sync_id}/resolve")
async def resolve_conflicts(
    sync_id: str,
    resolution: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Resolve conflicts in a synchronization process.
    
    Args:
        sync_id: Synchronization process identifier
        resolution: Conflict resolution rules
        db: Database session
        
    Returns:
        Dictionary with resolution status
    """
    try:
        resolver = ConflictResolver(db)
        result = await resolver.resolve_conflicts(sync_id, resolution)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to resolve conflicts: {str(e)}"
        ) 