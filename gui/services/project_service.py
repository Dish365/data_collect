from kivy.app import App
import threading
import uuid
import json
from datetime import datetime
from utils.cross_platform_toast import toast
from kivy.clock import Clock
import time

class ProjectService:
    def __init__(self, auth_service, db_service, sync_service):
        self.auth_service = auth_service
        self.db_service = db_service
        self.sync_service = sync_service

    def _safe_db_write(self, db_func, *args, **kwargs):
        """Execute database write operations with retry logic for locked databases"""
        max_retries = 5
        base_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                return db_func(*args, **kwargs)
            except Exception as e:
                error_msg = str(e).lower()
                if 'database is locked' in error_msg or 'database is busy' in error_msg:
                    if attempt < max_retries - 1:
                        # Exponential backoff
                        delay = base_delay * (2 ** attempt)
                        time.sleep(delay)
                        continue
                raise
        raise Exception("Database operation failed after multiple retries")

    def load_projects(self, search_query=None, limit=10, offset=0):
        """Load projects with API sync and local fallback"""
        conn = self.db_service.get_db_connection()
        try:
            # Try to sync with API on first load (offset=0) without search
            if offset == 0 and not search_query:
                self._sync_projects_from_api(conn)

            # Fetch from local DB with search and pagination
            projects_data = self._fetch_local_projects(conn, search_query, limit, offset)
            return projects_data, None
            
        except Exception as e:
            print(f"Error loading projects: {e}")
            return [], str(e)
        finally:
            if conn:
                conn.close()
    
    def _sync_projects_from_api(self, conn):
        """Sync projects from API to local database"""
        try:
            response = self.auth_service.make_authenticated_request('api/v1/projects/')
            if 'error' in response:
                return  # Skip sync if API unavailable
                
            api_projects = response if isinstance(response, list) else response.get('results', [])
            user_id = self.auth_service.get_user_data().get('id')
            cursor = conn.cursor()
            
            # Clean existing synced projects for this user
            if user_id:
                cursor.execute('DELETE FROM projects WHERE user_id = ? AND sync_status = ?', (user_id, 'synced'))
            else:
                cursor.execute('DELETE FROM projects WHERE sync_status = ?', ('synced',))
            
            # Insert fresh API data
            for project in api_projects:
                cursor.execute("""
                    INSERT OR REPLACE INTO projects 
                    (id, name, description, created_by, user_id, created_at, cloud_id, sync_status) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project.get('id'), 
                    project.get('name'), 
                    project.get('description', ''), 
                    project.get('created_by', 'unknown'), 
                    user_id, 
                    project.get('created_at', datetime.now().isoformat()), 
                    project.get('id'), 
                    'synced'
                ))
            conn.commit()
            
        except Exception as e:
            print(f"API sync failed: {e}")
            # Continue with local data only
    
    def _fetch_local_projects(self, conn, search_query, limit, offset):
        """Fetch projects from local database"""
        user_data = self.auth_service.get_user_data() if self.auth_service else None
        user_id = user_data.get('id') if user_data else None
        
        # Build query with proper user filtering
        if user_id:
            query = "SELECT * FROM projects WHERE user_id = ? AND sync_status != ?"
            params = [user_id, 'pending_delete']
        else:
            # If no user_id, fetch all projects (for unauthenticated state)
            query = "SELECT * FROM projects WHERE sync_status != ?"
            params = ['pending_delete']
        
        # Add search filter
        if search_query:
            query += " AND (name LIKE ? OR description LIKE ?)"
            search_term = f"%{search_query}%"
            params.extend([search_term, search_term])
        
        # Add ordering and pagination
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except Exception as e:
            print(f"Error executing query: {e}")
            return []

    def create_project(self, project_data):
        """Create a new project with API sync and local fallback"""
        def db_write():
            conn = self.db_service.get_db_connection()
            try:
                user_id = self.auth_service.get_user_data().get('id', 'unknown')
                api_data = {
                    'name': project_data['name'], 
                    'description': project_data['description'], 
                    'created_by': user_id
                }
                
                # Try API first
                response = self.auth_service.make_authenticated_request(
                    'api/v1/projects/', method='POST', data=api_data
                )
                
                cursor = conn.cursor()
                
                if 'error' in response:
                    # Offline mode - create locally and queue for sync
                    project_id = str(uuid.uuid4())
                    cursor.execute("""
                        INSERT INTO projects 
                        (id, name, description, created_by, user_id, created_at, sync_status) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        project_id, 
                        project_data['name'], 
                        project_data['description'], 
                        user_id, 
                        user_id, 
                        datetime.now().isoformat(),
                        'pending'
                    ))
                    
                    if self.sync_service:
                        self.sync_service.queue_sync('projects', project_id, 'create', api_data)
                    message = "Project created offline (will sync when online)"
                else:
                    # Online mode - save with cloud ID
                    project_id = response.get('id', str(uuid.uuid4()))
                    cursor.execute("""
                        INSERT INTO projects 
                        (id, name, description, created_by, user_id, created_at, cloud_id, sync_status) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        project_id, 
                        project_data['name'], 
                        project_data['description'], 
                        user_id, 
                        user_id, 
                        response.get('created_at', datetime.now().isoformat()),
                        project_id, 
                        'synced'
                    ))
                    message = "Project created successfully!"
                
                conn.commit()
                return {'message': message, 'reload': True, 'project_id': project_id}
            finally:
                conn.close()
        
        return self._safe_db_write(db_write)

    def update_project(self, project_id, project_data):
        """Update an existing project with API sync and local fallback"""
        def db_write():
            conn = self.db_service.get_db_connection()
            try:
                api_data = {
                    'name': project_data['name'], 
                    'description': project_data['description']
                }
                
                # Try API update
                response = self.auth_service.make_authenticated_request(
                    f'api/v1/projects/{project_id}/', method='PUT', data=api_data
                )
                
                cursor = conn.cursor()
                current_time = datetime.now().isoformat()
                
                if 'error' in response:
                    # Offline mode - update locally and queue for sync
                    cursor.execute("""
                        UPDATE projects 
                        SET name = ?, description = ?, updated_at = ?, sync_status = ? 
                        WHERE id = ?
                    """, (
                        project_data['name'], 
                        project_data['description'], 
                        current_time,
                        'pending', 
                        project_id
                    ))
                    
                    if self.sync_service:
                        self.sync_service.queue_sync('projects', project_id, 'update', api_data)
                    message = "Project updated offline (will sync when online)"
                else:
                    # Online mode - mark as synced
                    cursor.execute("""
                        UPDATE projects 
                        SET name = ?, description = ?, updated_at = ?, sync_status = ? 
                        WHERE id = ?
                    """, (
                        project_data['name'], 
                        project_data['description'], 
                        response.get('updated_at', current_time),
                        'synced', 
                        project_id
                    ))
                    message = "Project updated successfully!"
                
                conn.commit()
                return {'message': message, 'reload': True}
            finally:
                conn.close()
        
        return self._safe_db_write(db_write)

    def delete_project(self, project_id):
        """Delete a project with API sync and local fallback"""
        def db_write():
            conn = self.db_service.get_db_connection()
            try:
                # Try API deletion
                response = self.auth_service.make_authenticated_request(
                    f'api/v1/projects/{project_id}/', method='DELETE'
                )
                
                cursor = conn.cursor()
                
                if 'error' in response:
                    # Offline mode - mark for deletion and queue for sync
                    if self.sync_service:
                        self.sync_service.queue_sync('projects', project_id, 'delete', None)
                    cursor.execute(
                        "UPDATE projects SET sync_status = ?, updated_at = ? WHERE id = ?", 
                        ('pending_delete', datetime.now().isoformat(), project_id)
                    )
                    message = "Project queued for deletion (will sync when online)"
                else:
                    # Online mode - delete immediately
                    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
                    message = "Project deleted successfully"
                
                conn.commit()
                return {'message': message, 'reload': True}
            finally:
                conn.close()
        
        return self._safe_db_write(db_write) 