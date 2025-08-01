import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from kivy.clock import Clock
from services.auth_service import AuthService
from utils.cross_platform_toast import toast


class SyncService:
    """Unified sync service for Django-FastAPI pipeline"""
    
    def __init__(self, db_service):
        self.db_service = db_service
        self.auth_service = AuthService()
        
        # Configuration
        self.sync_interval = 300  # 5 minutes
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
        # State
        self.is_syncing = False
        self.sync_callbacks: List[Callable] = []
        
        # Start auto sync
        self._schedule_auto_sync()
    
    def add_sync_callback(self, callback: Callable) -> None:
        """Add callback to be called when sync completes"""
        if callback not in self.sync_callbacks:
            self.sync_callbacks.append(callback)
    
    def remove_sync_callback(self, callback: Callable) -> None:
        """Remove sync callback"""
        if callback in self.sync_callbacks:
            self.sync_callbacks.remove(callback)
    
    def _notify_callbacks(self, success: bool, results: Dict[str, Any]) -> None:
        """Notify all registered callbacks"""
        for callback in self.sync_callbacks:
            try:
                callback(success, results)
            except Exception as e:
                print(f"Error in sync callback: {e}")
    
    def _schedule_auto_sync(self) -> None:
        """Schedule automatic sync"""
        Clock.schedule_interval(self.auto_sync, self.sync_interval)
    
    def stop_auto_sync(self) -> None:
        """Stop automatic sync"""
        Clock.unschedule(self.auto_sync)
    
    def auto_sync(self, dt=None) -> None:
        """Automatic sync (non-blocking)"""
        if not self.is_syncing:
            self.sync_all()
    
    def get_pending_items(self) -> List[Dict[str, Any]]:
        """Get all pending sync items"""
        try:
            conn = self.db_service.get_db_connection()
            cursor = conn.cursor()
            
            user_id = self.auth_service.get_user_data().get('id')
            if user_id:
                cursor.execute('''
                    SELECT * FROM sync_queue 
                    WHERE status = 'pending' AND user_id = ?
                    ORDER BY priority DESC, created_at ASC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT * FROM sync_queue 
                    WHERE status = 'pending' 
                    ORDER BY priority DESC, created_at ASC
                ''')
            
            items = cursor.fetchall()
            return [dict(item) for item in items]
            
        except Exception as e:
            print(f"Error getting pending items: {e}")
            return []
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def get_sync_stats(self) -> Dict[str, int]:
        """Get sync statistics"""
        try:
            conn = self.db_service.get_db_connection()
            cursor = conn.cursor()
            
            user_id = self.auth_service.get_user_data().get('id')
            base_query = "SELECT status, COUNT(*) FROM sync_queue"
            
            if user_id:
                cursor.execute(f"{base_query} WHERE user_id = ? GROUP BY status", (user_id,))
            else:
                cursor.execute(f"{base_query} GROUP BY status")
            
            stats = {'pending': 0, 'completed': 0, 'failed': 0, 'syncing': 0}
            for status, count in cursor.fetchall():
                stats[status] = count
                
            return stats
            
        except Exception as e:
            print(f"Error getting sync stats: {e}")
            return {'pending': 0, 'completed': 0, 'failed': 0, 'syncing': 0}
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def sync_all(self) -> None:
        """Sync all pending items"""
        if self.is_syncing:
            return
        
        self.is_syncing = True
        pending_items = self.get_pending_items()
        
        if not pending_items:
            self.is_syncing = False
            self._notify_callbacks(True, {'message': 'No items to sync', 'synced_count': 0})
            return
        
        # Process items
        results = self._process_sync_batch(pending_items)
        self.is_syncing = False
        
        # Notify callbacks
        success = results.get('success_count', 0) > 0
        self._notify_callbacks(success, results)
    
    def sync_single_item(self, item: Dict[str, Any]) -> bool:
        """Sync a single item"""
        try:
            return self._process_sync_item(item)
        except Exception as e:
            print(f"Error syncing single item: {e}")
            return False
    
    def _process_sync_batch(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a batch of sync items"""
        results = {
            'total_count': len(items),
            'success_count': 0,
            'failed_count': 0,
            'errors': []
        }
        
        for item in items:
            try:
                if self._process_sync_item(item):
                    results['success_count'] += 1
                else:
                    results['failed_count'] += 1
            except Exception as e:
                results['failed_count'] += 1
                results['errors'].append(f"Item {item.get('id', 'unknown')}: {str(e)}")
        
        return results
    
    def _process_sync_item(self, item: Dict[str, Any]) -> bool:
        """Process a single sync item with the Django backend"""
        try:
            self._update_sync_status(item['id'], 'syncing')
            
            # Prepare sync data
            sync_data = {
                'table_name': item['table_name'],
                'record_id': item['record_id'],
                'operation': item['operation'],
                'data': json.loads(item['data']) if item['data'] else None,
                'priority': item.get('priority', 0)
            }
            
            # Send to Django sync endpoint
            response = self._send_to_django_sync(sync_data)
            
            if response and response.get('success', False):
                self._update_sync_status(item['id'], 'completed')
                return True
            else:
                error_msg = response.get('error', 'Unknown error') if response else 'No response'
                self._handle_sync_failure(item, error_msg)
                return False
                
        except Exception as e:
            self._handle_sync_failure(item, str(e))
            return False
    
    def _send_to_django_sync(self, sync_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send sync data to Django backend"""
        try:
            endpoint = 'api/sync/sync-queue/'
            
            response = self.auth_service.make_authenticated_request(
                endpoint,
                method='POST',
                data=sync_data
            )
            
            return response
            
        except Exception as e:
            print(f"Error sending to Django sync: {e}")
            return None
    
    def _update_sync_status(self, item_id: int, status: str, error_message: str = None) -> None:
        """Update sync item status in local database"""
        try:
            conn = self.db_service.get_db_connection()
            cursor = conn.cursor()
            
            if error_message:
                cursor.execute('''
                    UPDATE sync_queue 
                    SET status = ?, last_attempt = ?, error_message = ?
                    WHERE id = ?
                ''', (status, datetime.now(), error_message, item_id))
            else:
                cursor.execute('''
                    UPDATE sync_queue 
                    SET status = ?, last_attempt = ?
                    WHERE id = ?
                ''', (status, datetime.now(), item_id))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error updating sync status: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def _handle_sync_failure(self, item: Dict[str, Any], error_message: str) -> None:
        """Handle sync failure with retry logic"""
        attempts = item.get('attempts', 0) + 1
        
        if attempts < self.max_retries:
            # Retry later
            self._update_sync_status(item['id'], 'pending', error_message)
            self._increment_attempts(item['id'])
        else:
            # Mark as failed
            self._update_sync_status(item['id'], 'failed', error_message)
    
    def _increment_attempts(self, item_id: int) -> None:
        """Increment attempt count for sync item"""
        try:
            conn = self.db_service.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sync_queue 
                SET attempts = attempts + 1
                WHERE id = ?
            ''', (item_id,))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error incrementing attempts: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def queue_sync(self, table_name: str, record_id: str, operation: str, 
                   data: Dict[str, Any], priority: int = 0) -> bool:
        """Queue an item for sync"""
        try:
            conn = self.db_service.get_db_connection()
            cursor = conn.cursor()
            
            user_id = self.auth_service.get_user_data().get('id')
            
            cursor.execute('''
                INSERT INTO sync_queue (table_name, record_id, operation, data, user_id, priority)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                table_name, 
                record_id, 
                operation, 
                json.dumps(data) if data else None, 
                user_id,
                priority
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error queuing sync item: {e}")
            return False
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def clear_completed_items(self) -> int:
        """Clear completed sync items and return count"""
        try:
            conn = self.db_service.get_db_connection()
            cursor = conn.cursor()
            
            user_id = self.auth_service.get_user_data().get('id')
            
            if user_id:
                cursor.execute('''
                    DELETE FROM sync_queue 
                    WHERE status = 'completed' AND user_id = ?
                ''', (user_id,))
            else:
                cursor.execute('''
                    DELETE FROM sync_queue 
                    WHERE status = 'completed'
                ''')
            
            count = cursor.rowcount
            conn.commit()
            return count
            
        except Exception as e:
            print(f"Error clearing completed items: {e}")
            return 0
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def retry_failed_items(self) -> int:
        """Retry all failed items and return count"""
        try:
            conn = self.db_service.get_db_connection()
            cursor = conn.cursor()
            
            user_id = self.auth_service.get_user_data().get('id')
            
            if user_id:
                cursor.execute('''
                    UPDATE sync_queue 
                    SET status = 'pending', attempts = 0, error_message = NULL
                    WHERE status = 'failed' AND user_id = ?
                ''', (user_id,))
            else:
                cursor.execute('''
                    UPDATE sync_queue 
                    SET status = 'pending', attempts = 0, error_message = NULL
                    WHERE status = 'failed'
                ''')
            
            count = cursor.rowcount
            conn.commit()
            return count
            
        except Exception as e:
            print(f"Error retrying failed items: {e}")
            return 0
        finally:
            if 'conn' in locals() and conn:
                conn.close() 