import uuid
import json
from datetime import datetime
import time

class FormService:
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

    def load_questions(self, project_id):
        """Loads questions for a project, from API if online, otherwise from local DB."""
        # Try fetching from API first - use the correct endpoint
        response = self.auth_service.make_authenticated_request(f'api/forms/questions/?project_id={project_id}')

        conn = self.db_service.get_db_connection()
        try:
            if 'error' not in response:
                # Sync with local DB
                api_questions = response if isinstance(response, list) else response.get('results', [])
                self._sync_local_questions(conn, project_id, api_questions)

            # Always return from local DB to have a single source of truth for the UI
            # Add user filtering to ensure only user-specific data
            user_data = self.auth_service.get_user_data()
            user_id = user_data.get('id') if user_data else None
            cursor = conn.cursor()
            if user_id:
                cursor.execute("SELECT * FROM questions WHERE project_id = ? AND user_id = ? ORDER BY order_index", (project_id, user_id))
            else:
                cursor.execute("SELECT * FROM questions WHERE project_id = ? ORDER BY order_index", (project_id,))
            questions_data = [dict(row) for row in cursor.fetchall()]
            return questions_data, None
        except Exception as e:
            print(f"Error loading questions: {e}")
            return [], str(e)
        finally:
            if conn:
                conn.close()
    
    def _sync_local_questions(self, conn, project_id, api_questions):
        """Syncs local questions for a project with data from the API."""
        def db_write():
            cursor = conn.cursor()
            user_data = self.auth_service.get_user_data()
            user_id = user_data.get('id') if user_data else None
            # Clear existing non-pending questions for this project and user
            if user_id:
                cursor.execute("DELETE FROM questions WHERE project_id = ? AND user_id = ? AND sync_status != 'pending'", (project_id, user_id))
            else:
                cursor.execute("DELETE FROM questions WHERE project_id = ? AND sync_status != 'pending'", (project_id,))
            
            for q in api_questions:
                # Map the new response_type field to the local question_type field
                response_type = q.get('response_type', q.get('question_type', 'text_short'))
                cursor.execute("""
                    INSERT OR REPLACE INTO questions 
                    (id, project_id, question_text, question_type, options, validation_rules, order_index, user_id, sync_status) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (q.get('id'), project_id, q.get('question_text'), response_type,
                      json.dumps(q.get('options')), json.dumps(q.get('validation_rules')),
                      q.get('order_index'), user_id, 'synced'))
            conn.commit()
        
        self._safe_db_write(db_write)

    def save_questions(self, project_id, questions_to_save):
        """Saves the full list of questions for a project, handling online/offline sync with ResponseType support."""
        # Try online save first
        is_online = self.auth_service.is_authenticated()
        if is_online:
            # Prepare payload for bulk create with new response type structure
            payload = []
            for index, q_data in enumerate(questions_to_save):
                # Get response type - now we use response_type directly
                response_type = q_data.get('response_type', 'text_short')
                
                # Clean up options based on response type
                options = q_data.get('options', [])
                
                # For non-choice response types, don't send options
                if 'choice' not in response_type:
                    options = None
                    allow_multiple = False
                else:
                    # For choice response types, ensure options is a proper list
                    if not options or not isinstance(options, list):
                        options = []
                    # Filter out empty options
                    options = [opt.strip() for opt in options if opt and str(opt).strip()]
                    # If less than 2 options for choice response type, add defaults
                    if len(options) < 2:
                        options = ["Option 1", "Option 2"]
                    allow_multiple = q_data.get('allow_multiple', response_type == 'choice_multiple')
                
                # Prepare the payload with enhanced response type structure
                question_payload = {
                    'project': project_id,
                    'question_text': q_data['question_text'],
                    'response_type': response_type,  # Use the new response_type field
                    'options': options,
                    'allow_multiple': allow_multiple,
                    'validation_rules': q_data.get('validation_rules', {}),
                    'order_index': index,
                    'is_required': q_data.get('is_required', False),
                }
                
                # Add response type specific metadata
                if response_type == 'scale_rating':
                    question_payload['validation_rules'].update({
                        'min_value': q_data.get('min_value', 1),
                        'max_value': q_data.get('max_value', 5)
                    })
                elif 'numeric' in response_type:
                    question_payload['validation_rules'].update({
                        'data_type': 'integer' if response_type == 'numeric_integer' else 'decimal'
                    })
                elif response_type in ['date', 'datetime']:
                    question_payload['validation_rules'].update({
                        'format': 'date' if response_type == 'date' else 'datetime'
                    })
                elif response_type in ['image', 'audio', 'video', 'file']:
                    question_payload['validation_rules'].update({
                        'media_type': response_type,
                        'max_size_mb': q_data.get('max_size_mb', 50)
                    })
                elif response_type == 'geopoint':
                    question_payload['validation_rules'].update({
                        'requires_gps': True,
                        'accuracy_required': q_data.get('accuracy_required', False)
                    })
                
                payload.append(question_payload)
            
            # Make API call to save questions
            response = self.auth_service.make_authenticated_request(
                'api/forms/questions/bulk_create/',
                method='POST',
                data=payload
            )
            
            if 'error' not in response:
                # Save returned questions to local DB as synced
                def db_write():
                    conn = self.db_service.get_db_connection()
                    try:
                        cursor = conn.cursor()
                        user_data = self.auth_service.get_user_data()
                        user_id = user_data.get('id') if user_data else None
                        if user_id:
                            cursor.execute("DELETE FROM questions WHERE project_id = ? AND user_id = ?", (project_id, user_id))
                        else:
                            cursor.execute("DELETE FROM questions WHERE project_id = ?", (project_id,))
                        conn.commit()
                        
                        # The response is a list of created questions
                        for q in response:
                            # Map response_type back to question_type for local storage compatibility
                            question_type = q.get('response_type', q.get('question_type', 'text_short'))
                            cursor.execute("""
                                INSERT OR REPLACE INTO questions 
                                (id, project_id, question_text, question_type, options, validation_rules, order_index, user_id, sync_status) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                q.get('id'), project_id, q.get('question_text'), question_type,
                                json.dumps(q.get('options')), json.dumps(q.get('validation_rules')),
                                q.get('order_index'), user_id, 'synced'))
                        conn.commit()
                        return {'message': 'Form saved to backend with response types!', 'reload': True}
                    finally:
                        if conn:
                            conn.close()
                return self._safe_db_write(db_write)
            else:
                print(f"API error: {response}")
                # If error, fall through to offline logic
        
        # Offline or failed online save: fallback to local save and queue for sync
        def db_write():
            conn = self.db_service.get_db_connection()
            try:
                cursor = conn.cursor()
                user_data = self.auth_service.get_user_data()
                user_id = user_data.get('id') if user_data else None
                if user_id:
                    cursor.execute("DELETE FROM questions WHERE project_id = ? AND user_id = ?", (project_id, user_id))
                else:
                    cursor.execute("DELETE FROM questions WHERE project_id = ?", (project_id,))
                conn.commit()

                # Now, insert the new set of questions
                for index, q_data in enumerate(questions_to_save):
                    q_data['order_index'] = index
                    self._save_single_question(conn, project_id, q_data)
                return {'message': 'Form saved locally with response types (offline mode)', 'reload': True}
            finally:
                if conn:
                    conn.close()
        return self._safe_db_write(db_write)

    def _save_single_question(self, conn, project_id, q_data):
        """Saves a single question and queues it for sync if needed."""
        # Get response type from the data
        response_type = q_data.get('response_type', 'text_short')
        
        # Clean up options based on response type for API compatibility
        options = q_data.get('options', [])
        
        # For non-choice response types, don't include options in API data
        if 'choice' not in response_type:
            api_options = None
            api_allow_multiple = False
        else:
            # For choice response types, ensure options is a proper list
            if not options or not isinstance(options, list):
                api_options = []
            else:
                # Filter out empty options
                api_options = [opt.strip() for opt in options if opt and str(opt).strip()]
                # If less than 2 options for choice response type, add defaults
                if len(api_options) < 2:
                    api_options = ["Option 1", "Option 2"]
            api_allow_multiple = q_data.get('allow_multiple', response_type == 'choice_multiple')
        
        # Prepare API data with response type structure
        api_data = {
            'project': project_id,
            'question_text': q_data['question_text'],
            'response_type': response_type,  # Use the new response_type field
            'options': api_options,
            'allow_multiple': api_allow_multiple,
            'validation_rules': q_data.get('validation_rules', {}),
            'order_index': q_data['order_index'],
            'is_required': q_data.get('is_required', False)
        }

        # Add response type specific metadata to validation rules
        if response_type == 'scale_rating':
            api_data['validation_rules'].update({
                'min_value': q_data.get('min_value', 1),
                'max_value': q_data.get('max_value', 5)
            })
        elif 'numeric' in response_type:
            api_data['validation_rules'].update({
                'data_type': 'integer' if response_type == 'numeric_integer' else 'decimal'
            })
        elif response_type in ['date', 'datetime']:
            api_data['validation_rules'].update({
                'format': 'date' if response_type == 'date' else 'datetime'
            })
        elif response_type in ['image', 'audio', 'video', 'file']:
            api_data['validation_rules'].update({
                'media_type': response_type,
                'max_size_mb': q_data.get('max_size_mb', 50)
            })
        elif response_type == 'geopoint':
            api_data['validation_rules'].update({
                'requires_gps': True,
                'accuracy_required': q_data.get('accuracy_required', False)
            })

        # Save locally with the response_type as question_type for compatibility
        question_id = str(uuid.uuid4())
        user_data = self.auth_service.get_user_data()
        user_id = user_data.get('id') if user_data else None
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO questions (id, project_id, question_text, question_type, options, validation_rules, order_index, user_id, sync_status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (question_id, project_id, q_data['question_text'], response_type,
              json.dumps(q_data.get('options')), json.dumps(api_data['validation_rules']),
              q_data['order_index'], user_id, 'pending'))
        conn.commit()
        
        # Queue for sync with the API data
        self.sync_service.queue_sync('questions', question_id, 'create', api_data)

    def get_response_types(self):
        """Get available response types from the backend or return defaults."""
        try:
            response = self.auth_service.make_authenticated_request('api/v1/response_types/')
            if 'error' not in response:
                return response.get('results', response) if 'results' in response else response
        except Exception as e:
            print(f"Error fetching response types: {e}")
        
        # Return default response types if API call fails
        return self._get_default_response_types()
    
    def _get_default_response_types(self):
        """Get default response types when API is not available."""
        return [
            {
                'name': 'text_short',
                'display_name': 'Short Text',
                'description': 'Single line text input',
                'data_type': 'text',
                'supports_options': False,
                'supports_media': False,
                'supports_geolocation': False,
            },
            {
                'name': 'text_long',
                'display_name': 'Long Text',
                'description': 'Multi-line text input',
                'data_type': 'text',
                'supports_options': False,
                'supports_media': False,
                'supports_geolocation': False,
            },
            {
                'name': 'numeric_integer',
                'display_name': 'Number (Integer)',
                'description': 'Whole numbers only',
                'data_type': 'numeric',
                'supports_options': False,
                'supports_media': False,
                'supports_geolocation': False,
            },
            {
                'name': 'numeric_decimal',
                'display_name': 'Number (Decimal)',
                'description': 'Numbers with decimal places',
                'data_type': 'numeric',
                'supports_options': False,
                'supports_media': False,
                'supports_geolocation': False,
            },
            {
                'name': 'choice_single',
                'display_name': 'Single Choice',
                'description': 'Select one option from a list',
                'data_type': 'text',
                'supports_options': True,
                'supports_media': False,
                'supports_geolocation': False,
            },
            {
                'name': 'choice_multiple',
                'display_name': 'Multiple Choice',
                'description': 'Select multiple options from a list',
                'data_type': 'json',
                'supports_options': True,
                'supports_media': False,
                'supports_geolocation': False,
            },
            {
                'name': 'scale_rating',
                'display_name': 'Rating Scale',
                'description': 'Rate on a numeric scale',
                'data_type': 'numeric',
                'supports_options': False,
                'supports_media': False,
                'supports_geolocation': False,
            },
            {
                'name': 'date',
                'display_name': 'Date',
                'description': 'Date picker',
                'data_type': 'datetime',
                'supports_options': False,
                'supports_media': False,
                'supports_geolocation': False,
            },
            {
                'name': 'datetime',
                'display_name': 'Date & Time',
                'description': 'Date and time picker',
                'data_type': 'datetime',
                'supports_options': False,
                'supports_media': False,
                'supports_geolocation': False,
            },
            {
                'name': 'geopoint',
                'display_name': 'GPS Location',
                'description': 'Single GPS coordinate',
                'data_type': 'geospatial',
                'supports_options': False,
                'supports_media': False,
                'supports_geolocation': True,
            },
            {
                'name': 'image',
                'display_name': 'Photo/Image',
                'description': 'Take photo or upload image',
                'data_type': 'file',
                'supports_options': False,
                'supports_media': True,
                'supports_geolocation': False,
            },
            {
                'name': 'audio',
                'display_name': 'Audio Recording',
                'description': 'Record or upload audio',
                'data_type': 'file',
                'supports_options': False,
                'supports_media': True,
                'supports_geolocation': False,
            },
            {
                'name': 'barcode',
                'display_name': 'Barcode/QR Code',
                'description': 'Scan barcode or QR code',
                'data_type': 'text',
                'supports_options': False,
                'supports_media': False,
                'supports_geolocation': False,
            },
        ] 