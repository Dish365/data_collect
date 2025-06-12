import json
import requests
from datetime import datetime
from kivy.clock import Clock

class SyncService:
    def __init__(self):
        self.base_url = 'http://localhost:8000/api/v1'  # Change this to your backend URL
        self.sync_interval = 300  # 5 minutes
        self.is_syncing = False
    
    def start_auto_sync(self, db_service):
        """Start automatic sync with interval"""
        self.db_service = db_service
        Clock.schedule_interval(self.sync, self.sync_interval)
    
    def stop_auto_sync(self):
        """Stop automatic sync"""
        Clock.unschedule(self.sync)
    
    def sync(self, dt=None):
        """Sync local data with backend"""
        if self.is_syncing:
            return
        
        self.is_syncing = True
        try:
            # Get pending items from sync queue
            cursor = self.db_service.conn.cursor()
            cursor.execute('''
                SELECT * FROM sync_queue 
                WHERE status = 'pending' 
                ORDER BY created_at ASC
            ''')
            pending_items = cursor.fetchall()
            
            for item in pending_items:
                self._process_sync_item(item)
                
        except Exception as e:
            print(f"Sync error: {str(e)}")
        finally:
            self.is_syncing = False
    
    def _process_sync_item(self, item):
        """Process a single sync queue item"""
        try:
            data = json.loads(item['data'])
            endpoint = f"{self.base_url}/{item['table_name']}/"
            
            if item['operation'] == 'create':
                response = requests.post(endpoint, json=data)
            elif item['operation'] == 'update':
                response = requests.put(f"{endpoint}{item['record_id']}/", json=data)
            elif item['operation'] == 'delete':
                response = requests.delete(f"{endpoint}{item['record_id']}/")
            
            if response.status_code in (200, 201, 204):
                # Update sync status
                cursor = self.db_service.conn.cursor()
                cursor.execute('''
                    UPDATE sync_queue 
                    SET status = 'completed', 
                        last_attempt = ? 
                    WHERE id = ?
                ''', (datetime.now(), item['id']))
                self.db_service.conn.commit()
            else:
                # Update attempt count
                cursor = self.db_service.conn.cursor()
                cursor.execute('''
                    UPDATE sync_queue 
                    SET attempts = attempts + 1,
                        last_attempt = ? 
                    WHERE id = ?
                ''', (datetime.now(), item['id']))
                self.db_service.conn.commit()
                
        except Exception as e:
            print(f"Error processing sync item: {str(e)}")
    
    def queue_sync(self, table_name, record_id, operation, data):
        """Queue an item for sync"""
        cursor = self.db_service.conn.cursor()
        cursor.execute('''
            INSERT INTO sync_queue (table_name, record_id, operation, data)
            VALUES (?, ?, ?, ?)
        ''', (table_name, record_id, operation, json.dumps(data)))
        self.db_service.conn.commit() 