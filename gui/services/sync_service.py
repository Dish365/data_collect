import json
import requests
from datetime import datetime
from kivy.clock import Clock
from services.auth_service import AuthService

class SyncService:
    def __init__(self, db_service):
        self.db_service = db_service
        self.base_url = 'http://127.0.0.1:8000'  # Standardized backend URL
        self.sync_interval = 300  # 5 minutes
        self.is_syncing = False
        self.auth_service = AuthService()
        Clock.schedule_interval(self.sync, self.sync_interval)
    
    def stop_auto_sync(self):
        """Stop automatic sync"""
        Clock.unschedule(self.sync)
    
    def sync(self, dt=None):
        """Sync local data with backend"""
        if self.is_syncing:
            return
        
        self.is_syncing = True
        
        conn = None
        try:
            conn = self.db_service.get_db_connection()
            cursor = conn.cursor()
            user_id = self.auth_service.get_user_data().get('id')
            if user_id:
                cursor.execute('''
                    SELECT * FROM sync_queue 
                    WHERE status = 'pending' AND user_id = ?
                    ORDER BY created_at ASC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT * FROM sync_queue 
                    WHERE status = 'pending' 
                    ORDER BY created_at ASC
                ''')
            pending_items = cursor.fetchall()
            
            for item in pending_items:
                self._process_sync_item(item, conn)
                
        except Exception as e:
            print(f"Sync error: {str(e)}")
        finally:
            self.is_syncing = False
            if conn:
                conn.close()
    
    def _process_sync_item(self, item, conn):
        """Process a single sync queue item"""
        try:
            data = json.loads(item['data']) if item['data'] else None
            # Corrected endpoint to use the dedicated sync-queue
            endpoint = 'api/sync/sync-queue/'

            if item['operation'] == 'create':
                # For 'create', we can send the whole sync item data
                sync_data = {
                    'table_name': item['table_name'],
                    'record_id': item['record_id'],
                    'operation': item['operation'],
                    'data': data,
                    'status': 'pending'
                }
                response = self.auth_service.make_authenticated_request(
                    endpoint,
                    method='POST',
                    data=sync_data
                )
            elif item['operation'] in ['update', 'delete']:
                # For 'update' and 'delete', we target a specific sync item if the API supports it.
                # Assuming the backend can look up the sync record by an ID from the sync_queue table.
                # If the backend needs to process this differently, this might need adjustment.
                sync_item_id = item['id'] # Assuming 'id' is the primary key of the sync_queue table
                target_endpoint = f"{endpoint}{sync_item_id}/"

                request_data = {
                    'operation': item['operation'],
                    'data': data
                }

                if item['operation'] == 'update':
                    response = self.auth_service.make_authenticated_request(
                        target_endpoint,
                        method='PUT',
                        data=request_data
                    )
                else: # 'delete'
                    response = self.auth_service.make_authenticated_request(
                        target_endpoint,
                        method='DELETE'
                    )
            else:
                print(f"Unknown operation: {item['operation']}")
                return

            # Check if sync was successful
            if 'error' not in response:
                # Update sync status
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sync_queue 
                    SET status = 'completed', 
                        last_attempt = ? 
                    WHERE id = ?
                ''', (datetime.now(), item['id']))
                conn.commit()
            else:
                # Update attempt count
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sync_queue 
                    SET attempts = attempts + 1,
                        last_attempt = ? 
                    WHERE id = ?
                ''', (datetime.now(), item['id']))
                conn.commit()
                
        except Exception as e:
            print(f"Error processing sync item: {str(e)}")
    
    def queue_sync(self, table_name, record_id, operation, data):
        """Queue an item for sync"""
        conn = self.db_service.get_db_connection()
        try:
            cursor = conn.cursor()
            user_id = self.auth_service.get_user_data().get('id')
            cursor.execute('''
                INSERT INTO sync_queue (table_name, record_id, operation, data, user_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (table_name, record_id, operation, json.dumps(data) if data else None, user_id))
            conn.commit()
        finally:
            conn.close() 