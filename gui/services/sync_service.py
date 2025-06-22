import json
import requests
from datetime import datetime
from kivy.clock import Clock
from services.auth_service import AuthService

class SyncService:
    def __init__(self, db_service):
        self.db_service = db_service
        self.base_url = 'http://localhost:8000'  # Change this to your backend URL
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
            endpoint = f"api/v1/{item['table_name']}/"
            
            if item['operation'] == 'create':
                response = self.auth_service.make_authenticated_request(
                    endpoint, 
                    method='POST', 
                    data=data
                )
            elif item['operation'] == 'update':
                response = self.auth_service.make_authenticated_request(
                    f"{endpoint}{item['record_id']}/", 
                    method='PUT', 
                    data=data
                )
            elif item['operation'] == 'delete':
                response = self.auth_service.make_authenticated_request(
                    f"{endpoint}{item['record_id']}/", 
                    method='DELETE'
                )
            
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
            cursor.execute('''
                INSERT INTO sync_queue (table_name, record_id, operation, data)
                VALUES (?, ?, ?, ?)
            ''', (table_name, record_id, operation, json.dumps(data) if data else None))
            conn.commit()
        finally:
            conn.close() 