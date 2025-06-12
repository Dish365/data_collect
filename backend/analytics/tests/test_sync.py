"""
Tests for data synchronization functionality.
"""

import pytest
from datetime import datetime
from ..sync.manager import SyncManager
from ..sync.conflict_resolver import ConflictResolver

@pytest.fixture
def mock_db():
    """Mock database session."""
    class MockDB:
        def execute(self, query):
            return None
    return MockDB()

@pytest.fixture
def sync_manager(mock_db):
    """Sync manager instance for testing."""
    return SyncManager(mock_db)

@pytest.fixture
def conflict_resolver(mock_db):
    """Conflict resolver instance for testing."""
    return ConflictResolver(mock_db)

@pytest.mark.asyncio
async def test_start_sync(sync_manager):
    """Test starting a sync process."""
    sync_id = await sync_manager.start_sync("source", "target")
    
    assert isinstance(sync_id, str)
    assert len(sync_id) > 0
    
    status = await sync_manager.get_status(sync_id)
    assert status["source"] == "source"
    assert status["target"] == "target"
    assert status["status"] == "running"

@pytest.mark.asyncio
async def test_get_sync_status(sync_manager):
    """Test getting sync status."""
    sync_id = await sync_manager.start_sync("source", "target")
    status = await sync_manager.get_status(sync_id)
    
    assert isinstance(status, dict)
    assert "status" in status
    assert "progress" in status
    assert "started_at" in status

@pytest.mark.asyncio
async def test_resolve_conflicts(conflict_resolver):
    """Test conflict resolution."""
    sync_id = "test-sync-id"
    resolution = {
        "strategy": "source_wins",
        "rules": {
            "field1": "keep_source",
            "field2": "keep_target"
        }
    }
    
    result = await conflict_resolver.resolve_conflicts(sync_id, resolution)
    
    assert isinstance(result, dict)
    assert result["status"] == "resolved"
    assert result["sync_id"] == sync_id
    assert "resolved_at" in result 