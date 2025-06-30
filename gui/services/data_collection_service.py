import uuid
import json
from datetime import datetime
import time

class DataCollectionService:
    def __init__(self, auth_service, db_service, sync_service):
        self.auth_service = auth_service
        self.db_service = db_service
        self.sync_service = sync_service

    def _safe_db_write(self, db_func, *args, **kwargs):
        """Executes a database write operation with retry logic for locked databases."""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                return db_func(*args, **kwargs)
            except Exception as e:
                if 'database is locked' in str(e):
                    time.sleep(0.2)
                else:
                    raise
        raise Exception("Database is locked after several retries.")

    def generate_respondent_id(self, project_id):
        """Generate a unique respondent ID for the project"""
        # Use timestamp + random component for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = str(uuid.uuid4())[:8]
        return f"RESP_{timestamp}_{random_suffix}"

    def create_respondent(self, project_id, name=None, email=None, phone=None, 
                         demographics=None, location_data=None, is_anonymous=True, 
                         consent_given=False):
        """Create a new respondent for data collection"""
        
        respondent_id = self.generate_respondent_id(project_id)
        user_data = self.auth_service.get_user_data()
        created_by = user_data.get('id') if user_data else None
        
        respondent_data = {
            'id': str(uuid.uuid4()),
            'respondent_id': respondent_id,
            'project': project_id,
            'name': name or '',
            'email': email or '',
            'phone': phone or '',
            'demographics': json.dumps(demographics or {}),
            'location_data': json.dumps(location_data or {}),
            'is_anonymous': is_anonymous,
            'consent_given': consent_given,
            'created_by': created_by,
            'sync_status': 'pending'
        }
        
        # Try to save to backend first if online
        if self.auth_service.is_authenticated():
            backend_data = {
                'respondent_id': respondent_id,
                'project': project_id,
                'name': name or '',
                'email': email or '',
                'phone': phone or '',
                'demographics': demographics or {},
                'location_data': location_data or {},
                'is_anonymous': is_anonymous,
                'consent_given': consent_given
            }
            
            response = self.auth_service.make_authenticated_request(
                'api/v1/respondents/',
                method='POST',
                data=backend_data
            )
            
            if 'error' not in response:
                # Successfully created on backend, save as synced
                respondent_data['sync_status'] = 'synced'
                respondent_data['id'] = response.get('id', respondent_data['id'])
        
        # Save to local database
        def db_write():
            conn = self.db_service.get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO respondents 
                    (id, respondent_id, project_id, name, email, phone, demographics, 
                     location_data, is_anonymous, consent_given, created_by, sync_status, user_id) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    respondent_data['id'], respondent_data['respondent_id'], project_id,
                    respondent_data['name'], respondent_data['email'], respondent_data['phone'],
                    respondent_data['demographics'], respondent_data['location_data'],
                    respondent_data['is_anonymous'], respondent_data['consent_given'],
                    respondent_data['created_by'], respondent_data['sync_status'], created_by
                ))
                conn.commit()
                
                # Queue for sync if not already synced
                if respondent_data['sync_status'] == 'pending':
                    sync_data = {
                        'respondent_id': respondent_id,
                        'project': project_id,
                        'name': name or '',
                        'email': email or '',
                        'phone': phone or '',
                        'demographics': demographics or {},
                        'location_data': location_data or {},
                        'is_anonymous': is_anonymous,
                        'consent_given': consent_given
                    }
                    self.sync_service.queue_sync('respondents', respondent_data['id'], 'create', sync_data)
                
                return respondent_data
            finally:
                if conn:
                    conn.close()
        
        return self._safe_db_write(db_write)

    def submit_form_responses(self, project_id, respondent_id, responses_data, 
                            location_data=None, device_info=None):
        """Submit all responses for a form completion"""
        
        user_data = self.auth_service.get_user_data()
        collected_by = user_data.get('id') if user_data else None
        
        saved_responses = []
        
        for response_data in responses_data:
            response_id = str(uuid.uuid4())
            
            # Prepare response data
            response_entry = {
                'response_id': response_id,
                'project': project_id,
                'question': response_data['question_id'],
                'respondent': respondent_id,
                'response_value': response_data['response_value'],
                'response_metadata': json.dumps(response_data.get('metadata', {})),
                'location_data': json.dumps(location_data or {}),
                'device_info': json.dumps(device_info or {}),
                'collected_by': collected_by,
                'sync_status': 'pending'
            }
            
            # Initialize backend_data as None
            backend_data = None
            
            # Try to save to backend first if online
            if self.auth_service.is_authenticated():
                # First get the respondent UUID from backend
                respondent_response = self.auth_service.make_authenticated_request(
                    f'api/v1/respondents/?respondent_id={respondent_id}'
                )
                
                respondent_uuid = None
                if 'error' not in respondent_response and 'results' in respondent_response:
                    results = respondent_response['results']
                    if results:
                        respondent_uuid = results[0]['id']
                
                if respondent_uuid:
                    backend_data = {
                        'project': project_id,
                        'question': response_data['question_id'],
                        'respondent': respondent_uuid,  # Use UUID instead of respondent_id
                        'response_value': response_data['response_value'],
                        'response_metadata': response_data.get('metadata', {}),
                        'location_data': location_data or {},
                        'device_info': device_info or {}
                    }
                else:
                    # Skip backend save if we can't find the respondent
                    backend_data = None
                
                if backend_data:
                    response = self.auth_service.make_authenticated_request(
                        'api/v1/responses/',
                        method='POST',
                        data=backend_data
                    )
                    
                    if 'error' not in response:
                        # Successfully created on backend
                        response_entry['sync_status'] = 'synced'
                        response_entry['response_id'] = response.get('response_id', response_entry['response_id'])
                    else:
                        print(f"Backend response error: {response}")
                else:
                    print("Skipping backend save - respondent not found on server")
            
            # Save to local database
            def db_write():
                conn = self.db_service.get_db_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO responses 
                        (response_id, project_id, question_id, respondent_id, response_value, 
                         response_metadata, location_data, device_info, collected_by, sync_status, user_id) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        response_entry['response_id'], project_id, response_data['question_id'],
                        respondent_id, response_data['response_value'], response_entry['response_metadata'],
                        response_entry['location_data'], response_entry['device_info'],
                        collected_by, response_entry['sync_status'], collected_by
                    ))
                    conn.commit()
                    
                    # Queue for sync if not already synced and we have valid backend data
                    if response_entry['sync_status'] == 'pending' and backend_data:
                        self.sync_service.queue_sync('responses', response_entry['response_id'], 'create', backend_data)
                    
                    return response_entry
                finally:
                    if conn:
                        conn.close()
            
            saved_response = self._safe_db_write(db_write)
            saved_responses.append(saved_response)
        
        # Update respondent's last_response_at in local database
        def update_respondent():
            conn = self.db_service.get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE respondents 
                    SET last_response_at = datetime('now') 
                    WHERE respondent_id = ?
                """, (respondent_id,))
                conn.commit()
            finally:
                if conn:
                    conn.close()
        
        self._safe_db_write(update_respondent)
        
        return {
            'respondent_id': respondent_id,
            'responses_count': len(saved_responses),
            'message': f'Form completed successfully! {len(saved_responses)} responses saved.'
        }

    def get_project_respondents(self, project_id):
        """Get all respondents for a project"""
        conn = self.db_service.get_db_connection()
        try:
            cursor = conn.cursor()
            user_data = self.auth_service.get_user_data()
            user_id = user_data.get('id') if user_data else None
            
            if user_id:
                cursor.execute("""
                    SELECT * FROM respondents 
                    WHERE project_id = ? AND user_id = ? 
                    ORDER BY created_at DESC
                """, (project_id, user_id))
            else:
                cursor.execute("""
                    SELECT * FROM respondents 
                    WHERE project_id = ? 
                    ORDER BY created_at DESC
                """, (project_id,))
            
            respondents = [dict(row) for row in cursor.fetchall()]
            return respondents, None
        except Exception as e:
            print(f"Error getting project respondents: {e}")
            return [], str(e)
        finally:
            if conn:
                conn.close()

    def get_respondent_responses(self, respondent_id):
        """Get all responses for a specific respondent"""
        conn = self.db_service.get_db_connection()
        try:
            cursor = conn.cursor()
            # Use LEFT JOIN to handle cases where questions might not exist in the database
            cursor.execute("""
                SELECT r.*, 
                       COALESCE(q.question_text, 'Unknown Question') as question_text, 
                       COALESCE(q.question_type, 'text') as question_type
                FROM responses r
                LEFT JOIN questions q ON r.question_id = q.id
                WHERE r.respondent_id = ?
                ORDER BY r.collected_at
            """, (respondent_id,))
            
            responses = [dict(row) for row in cursor.fetchall()]
            return responses, None
        except Exception as e:
            print(f"Error getting respondent responses: {e}")
            return [], str(e)
        finally:
            if conn:
                conn.close() 