from kivy.app import App
import threading
import uuid
import json
from datetime import datetime
from kivymd.toast import toast
from kivy.clock import Clock
import time

class ProjectService:
    def __init__(self, auth_service, db_service, sync_service):
        self.auth_service = auth_service
        self.db_service = db_service
        self.sync_service = sync_service

    def _safe_db_write(self, db_func, *args, **kwargs):
        max_retries = 5
        for attempt in range(max_retries):
            try:
                return db_func(*args, **kwargs)
            except Exception as e:
                if 'database is locked' in str(e):
                    time.sleep(0.2)
                else:
                    raise
        raise Exception("Database is locked after several retries")

    def load_projects(self, search_query=None, limit=10, offset=0):
        conn = self.db_service.get_db_connection()
        try:
            # Try to fetch from API first (if online and no search)
            if offset == 0 and not search_query:
                response = self.auth_service.make_authenticated_request('api/v1/projects/')
                if 'error' not in response:
                    # Sync with local DB
                    api_projects = response if isinstance(response, list) else response.get('results', [])
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM projects WHERE sync_status != ?', ('pending',))
                    for project in api_projects:
                         cursor.execute("""
                            INSERT OR REPLACE INTO projects 
                            (id, name, description, created_by, created_at, cloud_id, sync_status) 
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                         """, (project.get('id'), project.get('name'), project.get('description', ''), 
                               project.get('created_by', 'unknown'), project.get('created_at', datetime.now().isoformat()), 
                               project.get('id'), 'synced'))
                    conn.commit()

            # Fetch from local DB with search and pagination
            query = "SELECT * FROM projects WHERE sync_status != 'pending_delete'"
            params = []
            if search_query:
                query += " AND name LIKE ?"
                params.append(f"%{search_query}%")
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor = conn.cursor()
            cursor.execute(query, params)
            projects_data = [dict(row) for row in cursor.fetchall()]
            
            return projects_data, None
        except Exception as e:
            return [], str(e)
        finally:
            if conn:
                conn.close()

    def create_project(self, project_data):
        def db_write():
            conn = self.db_service.get_db_connection()
            try:
                user_id = self.auth_service.get_user_data().get('id', 'unknown')
                api_data = {'name': project_data['name'], 'description': project_data['description'], 'created_by': user_id}
                response = self.auth_service.make_authenticated_request('api/v1/projects/', method='POST', data=api_data)
                cursor = conn.cursor()
                if 'error' in response:
                    project_id = str(uuid.uuid4())
                    cursor.execute("INSERT INTO projects (id, name, description, created_by, sync_status) VALUES (?, ?, ?, ?, ?)",
                                   (project_id, project_data['name'], project_data['description'], api_data['created_by'], 'pending'))
                    self.sync_service.queue_sync('projects', project_id, 'create', api_data)
                    message = "Project created (will sync when online)"
                else:
                    project_id = response.get('id', str(uuid.uuid4()))
                    cursor.execute("INSERT INTO projects (id, name, description, created_by, cloud_id, sync_status) VALUES (?, ?, ?, ?, ?, ?)",
                                   (project_id, project_data['name'], project_data['description'], api_data['created_by'], project_id, 'synced'))
                    message = "Project created successfully!"
                conn.commit()
                return {'message': message, 'reload': True}
            finally:
                conn.close()
        return self._safe_db_write(db_write)

    def update_project(self, project_id, project_data):
        def db_write():
            conn = self.db_service.get_db_connection()
            try:
                api_data = {'name': project_data['name'], 'description': project_data['description']}
                response = self.auth_service.make_authenticated_request(f'api/v1/projects/{project_id}/', method='PUT', data=api_data)
                cursor = conn.cursor()
                if 'error' in response:
                    cursor.execute("UPDATE projects SET name = ?, description = ?, sync_status = ? WHERE id = ?",
                                   (project_data['name'], project_data['description'], 'pending', project_id))
                    self.sync_service.queue_sync('projects', project_id, 'update', api_data)
                    message = "Project updated (will sync when online)"
                else:
                    cursor.execute("UPDATE projects SET name = ?, description = ?, sync_status = ? WHERE id = ?",
                                   (project_data['name'], project_data['description'], 'synced', project_id))
                    message = "Project updated successfully!"
                conn.commit()
                return {'message': message, 'reload': True}
            finally:
                conn.close()
        return self._safe_db_write(db_write)

    def delete_project(self, project_id):
        def db_write():
            conn = self.db_service.get_db_connection()
            try:
                response = self.auth_service.make_authenticated_request(f'api/v1/projects/{project_id}/', method='DELETE')
                cursor = conn.cursor()
                if 'error' in response:
                    self.sync_service.queue_sync('projects', project_id, 'delete', None)
                    cursor.execute("UPDATE projects SET sync_status = ? WHERE id = ?", ('pending_delete', project_id))
                    message = "Project queued for deletion"
                else:
                    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
                    message = "Project deleted successfully"
                conn.commit()
                return {'message': message, 'reload': True}
            finally:
                conn.close()
        return self._safe_db_write(db_write) 