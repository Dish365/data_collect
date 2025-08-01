import uuid
import json
from datetime import datetime
import time
from typing import List, Dict, Tuple, Optional, Any

class ModernFormService:
    """Streamlined, modern form service with optimized performance"""
    
    def __init__(self, auth_service, db_service, sync_service):
        self.auth_service = auth_service
        self.db_service = db_service
        self.sync_service = sync_service
        
        # Cache for better performance
        self._questions_cache = {}
        self._cache_timeout = 300  # 5 minutes
    
    def load_questions(self, project_id: str) -> Tuple[List[Dict], Optional[str]]:
        """Load questions for a project with caching and error handling"""
        try:
            print(f"DEBUG: load_questions called for project_id: {project_id}")
            
            # Check cache first
            cache_key = f"questions_{project_id}"
            if self._is_cache_valid(cache_key):
                cached_data = self._questions_cache[cache_key]['data']
                print(f"DEBUG: Returning {len(cached_data)} cached questions")
                return cached_data, None
            
            # Try API first
            print(f"DEBUG: Cache miss, loading from API...")
            questions = self._load_from_api(project_id)
            
            # Fallback to local database if API fails
            if not questions:
                print(f"DEBUG: API returned no questions, trying local database...")
                questions = self._load_from_local_db(project_id)
                print(f"DEBUG: Local DB returned {len(questions)} questions")
            
            # Cache the results
            self._cache_questions(cache_key, questions)
            
            print(f"DEBUG: Final result: {len(questions)} questions loaded")
            return questions, None
            
        except Exception as e:
            error_msg = f"Failed to load questions: {str(e)}"
            print(f"ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            return [], error_msg
    
    def save_questions(self, project_id: str, questions: List[Dict]) -> Dict[str, Any]:
        """Save questions with optimized sync strategy"""
        try:
            # Validate input
            if not project_id or not questions:
                raise ValueError("Project ID and questions are required")
            
            # Validate questions
            validated_questions = self._validate_questions(questions)
            
            # Try online save first
            if self.auth_service.is_authenticated():
                try:
                    result = self._save_to_api(project_id, validated_questions)
                    if result:
                        # Clear cache on successful save
                        self._clear_cache(f"questions_{project_id}")
                        return {'message': 'Form saved successfully!', 'status': 'synced'}
                except Exception as api_error:
                    print(f"API save failed: {api_error}")
                    # Continue to offline save
            
            # Offline save with sync queue
            self._save_to_local_db(project_id, validated_questions)
            self._queue_for_sync(project_id, validated_questions)
            
            # Clear cache
            self._clear_cache(f"questions_{project_id}")
            
            return {'message': 'Form saved locally (will sync when online)', 'status': 'offline'}
            
        except Exception as e:
            error_msg = f"Failed to save questions: {str(e)}"
            print(error_msg)
            return {'error': error_msg, 'status': 'error'}
    
    def get_response_types(self) -> List[Dict[str, Any]]:
        """Get available response types with caching"""
        cache_key = "response_types"
        
        if self._is_cache_valid(cache_key):
            return self._questions_cache[cache_key]['data']
        
        try:
            # Try API first
            response = self.auth_service.make_authenticated_request('api/v1/response_types/')
            if 'error' not in response:
                types = response.get('results', response) if 'results' in response else response
                self._cache_questions(cache_key, types)
                return types
        except Exception as e:
            print(f"Error fetching response types from API: {e}")
        
        # Fallback to defaults
        default_types = self._get_default_response_types()
        self._cache_questions(cache_key, default_types)
        return default_types
    
    def delete_question(self, project_id: str, question_id: str) -> Dict[str, Any]:
        """Delete a specific question"""
        try:
            # Try API first
            if self.auth_service.is_authenticated():
                try:
                    response = self.auth_service.make_authenticated_request(
                        f'api/v1/questions/{question_id}/',
                        method='DELETE'
                    )
                    if 'error' not in response:
                        self._clear_cache(f"questions_{project_id}")
                        return {'message': 'Question deleted successfully', 'status': 'synced'}
                except Exception as api_error:
                    print(f"API delete failed: {api_error}")
            
            # Delete from local database
            self._delete_from_local_db(question_id)
            
            # Queue for sync
            self.sync_service.queue_sync('questions', question_id, 'delete', {})
            
            # Clear cache
            self._clear_cache(f"questions_{project_id}")
            
            return {'message': 'Question deleted locally (will sync when online)', 'status': 'offline'}
            
        except Exception as e:
            error_msg = f"Failed to delete question: {str(e)}"
            print(error_msg)
            return {'error': error_msg, 'status': 'error'}
    
    # Private methods
    def _load_from_api(self, project_id: str) -> List[Dict]:
        """Load questions from API with enhanced debugging"""
        try:
            endpoint = f'api/v1/questions/?project_id={project_id}&page_size=100&ordering=order_index'
            print(f"DEBUG: API request to: {endpoint}")
            
            response = self.auth_service.make_authenticated_request(endpoint)
            print(f"DEBUG: API response type: {type(response)}")
            print(f"DEBUG: API response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
            
            if 'error' not in response:
                api_questions = response if isinstance(response, list) else response.get('results', [])
                print(f"DEBUG: Found {len(api_questions)} questions from API")
                
                if api_questions:
                    print(f"DEBUG: First API question: {api_questions[0]}")
                
                # Sync to local database
                self._sync_to_local_db(project_id, api_questions)
                
                normalized = self._normalize_questions(api_questions)
                print(f"DEBUG: Normalized to {len(normalized)} questions")
                return normalized
            else:
                print(f"DEBUG: API returned error: {response.get('error')}")
        except Exception as e:
            print(f"ERROR: Exception loading from API: {e}")
            import traceback
            traceback.print_exc()
        
        return []
    
    def _load_from_local_db(self, project_id: str) -> List[Dict]:
        """Load questions from local database"""
        conn = self.db_service.get_db_connection()
        try:
            cursor = conn.cursor()
            user_data = self.auth_service.get_user_data()
            user_id = user_data.get('id') if user_data else None
            
            if user_id:
                cursor.execute(
                    "SELECT * FROM questions WHERE project_id = ? AND user_id = ? ORDER BY order_index",
                    (project_id, user_id)
                )
            else:
                cursor.execute(
                    "SELECT * FROM questions WHERE project_id = ? ORDER BY order_index",
                    (project_id,)
                )
            
            questions = [dict(row) for row in cursor.fetchall()]
            return self._normalize_questions(questions)
            
        except Exception as e:
            print(f"Error loading from local DB: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def _save_to_api(self, project_id: str, questions: List[Dict]) -> bool:
        """Save questions to API"""
        payload = []
        for index, question in enumerate(questions):
            question_payload = {
                'project': project_id,
                'question_text': question['question_text'],
                'response_type': question['response_type'],
                'options': question.get('options'),
                'allow_multiple': question.get('allow_multiple', False),
                'validation_rules': question.get('validation_rules', {}),
                'order_index': index,
                'is_required': question.get('is_required', True)
            }
            
            # Add response type specific validation rules
            self._add_validation_rules(question_payload, question)
            payload.append(question_payload)
        
        response = self.auth_service.make_authenticated_request(
            'api/v1/questions/bulk_create/',
            method='POST',
            data=payload
        )
        
        if 'error' not in response:
            # Update local database with returned data
            self._sync_to_local_db(project_id, response)
            return True
        
        return False
    
    def _save_to_local_db(self, project_id: str, questions: List[Dict]):
        """Save questions to local database"""
        conn = self.db_service.get_db_connection()
        try:
            cursor = conn.cursor()
            user_data = self.auth_service.get_user_data()
            user_id = user_data.get('id') if user_data else None
            
            # Clear existing questions
            if user_id:
                cursor.execute("DELETE FROM questions WHERE project_id = ? AND user_id = ?", (project_id, user_id))
            else:
                cursor.execute("DELETE FROM questions WHERE project_id = ?", (project_id,))
            
            # Insert new questions
            for index, question in enumerate(questions):
                question_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO questions 
                    (id, project_id, question_text, question_type, options, validation_rules, 
                     order_index, user_id, sync_status, is_required) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    question_id,
                    project_id,
                    question['question_text'],
                    question['response_type'],
                    json.dumps(question.get('options')),
                    json.dumps(question.get('validation_rules', {})),
                    index,
                    user_id,
                    'pending',
                    question.get('is_required', True)
                ))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error saving to local DB: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _sync_to_local_db(self, project_id: str, api_questions: List[Dict]):
        """Sync API questions to local database"""
        conn = self.db_service.get_db_connection()
        try:
            cursor = conn.cursor()
            user_data = self.auth_service.get_user_data()
            user_id = user_data.get('id') if user_data else None
            
            # Clear existing synced questions
            if user_id:
                cursor.execute(
                    "DELETE FROM questions WHERE project_id = ? AND user_id = ? AND sync_status != 'pending'",
                    (project_id, user_id)
                )
            else:
                cursor.execute(
                    "DELETE FROM questions WHERE project_id = ? AND sync_status != 'pending'",
                    (project_id,)
                )
            
            # Insert API questions
            for question in api_questions:
                response_type = question.get('response_type', question.get('question_type', 'text_short'))
                cursor.execute("""
                    INSERT OR REPLACE INTO questions 
                    (id, project_id, question_text, question_type, options, validation_rules, 
                     order_index, user_id, sync_status, is_required) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    question.get('id'),
                    project_id,
                    question.get('question_text'),
                    response_type,
                    json.dumps(question.get('options')),
                    json.dumps(question.get('validation_rules')),
                    question.get('order_index'),
                    user_id,
                    'synced',
                    question.get('is_required', True)
                ))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error syncing to local DB: {e}")
        finally:
            if conn:
                conn.close()
    
    def _delete_from_local_db(self, question_id: str):
        """Delete question from local database"""
        conn = self.db_service.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
            conn.commit()
        except Exception as e:
            print(f"Error deleting from local DB: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _queue_for_sync(self, project_id: str, questions: List[Dict]):
        """Queue questions for sync when online"""
        try:
            for index, question in enumerate(questions):
                question_data = {
                    'project': project_id,
                    'question_text': question['question_text'],
                    'response_type': question['response_type'],
                    'options': question.get('options'),
                    'allow_multiple': question.get('allow_multiple', False),
                    'validation_rules': question.get('validation_rules', {}),
                    'order_index': index,
                    'is_required': question.get('is_required', True)
                }
                
                self.sync_service.queue_sync(
                    'questions',
                    str(uuid.uuid4()),
                    'create',
                    question_data
                )
        except Exception as e:
            print(f"Error queueing for sync: {e}")
    
    def _validate_questions(self, questions: List[Dict]) -> List[Dict]:
        """Validate and clean question data"""
        validated = []
        
        for question in questions:
            # Required fields
            if not question.get('question_text', '').strip():
                raise ValueError("Question text is required")
            
            if not question.get('response_type'):
                raise ValueError("Response type is required")
            
            # Clean options for choice types
            if question['response_type'] in ['choice_single', 'choice_multiple']:
                options = question.get('options', [])
                if isinstance(options, str):
                    try:
                        options = json.loads(options)
                    except:
                        options = []
                
                # Filter and validate options
                clean_options = [opt.strip() for opt in options if opt and str(opt).strip()]
                if len(clean_options) < 2:
                    raise ValueError(f"Choice questions need at least 2 options")
                
                question['options'] = clean_options
                question['allow_multiple'] = question['response_type'] == 'choice_multiple'
            else:
                question['options'] = None
                question['allow_multiple'] = False
            
            validated.append(question)
        
        return validated
    
    def _normalize_questions(self, questions: List[Dict]) -> List[Dict]:
        """Normalize questions from different sources"""
        normalized = []
        
        for question in questions:
            # Parse JSON fields
            options = question.get('options')
            if options and isinstance(options, str):
                try:
                    options = json.loads(options)
                except:
                    options = []
            
            validation_rules = question.get('validation_rules')
            if validation_rules and isinstance(validation_rules, str):
                try:
                    validation_rules = json.loads(validation_rules)
                except:
                    validation_rules = {}
            
            # Normalize field names
            normalized_question = {
                'id': question.get('id'),
                'question_text': question.get('question_text', ''),
                'response_type': question.get('response_type') or question.get('question_type', 'text_short'),
                'options': options,
                'validation_rules': validation_rules,
                'order_index': question.get('order_index', 0),
                'is_required': question.get('is_required', True),
                'allow_multiple': question.get('allow_multiple', False)
            }
            
            normalized.append(normalized_question)
        
        return normalized
    
    def _add_validation_rules(self, payload: Dict, question: Dict):
        """Add response type specific validation rules"""
        response_type = question['response_type']
        validation_rules = payload['validation_rules']
        
        if response_type == 'scale_rating':
            validation_rules.update({
                'min_value': question.get('min_value', 1),
                'max_value': question.get('max_value', 5)
            })
        elif 'numeric' in response_type:
            validation_rules.update({
                'data_type': 'integer' if response_type == 'numeric_integer' else 'decimal'
            })
        elif response_type in ['date', 'datetime']:
            validation_rules.update({
                'format': 'date' if response_type == 'date' else 'datetime'
            })
        elif response_type in ['image', 'audio', 'video', 'file']:
            validation_rules.update({
                'media_type': response_type,
                'max_size_mb': question.get('max_size_mb', 50)
            })
        elif response_type == 'geopoint':
            validation_rules.update({
                'requires_gps': True,
                'accuracy_required': question.get('accuracy_required', False)
            })
    
    def _get_default_response_types(self) -> List[Dict[str, Any]]:
        """Get default response types when API is unavailable"""
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
                'name': 'geoshape',
                'display_name': 'GPS Area',
                'description': 'GPS polygon/area boundary',
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
                'name': 'video',
                'display_name': 'Video Recording',
                'description': 'Record or upload video',
                'data_type': 'file',
                'supports_options': False,
                'supports_media': True,
                'supports_geolocation': False,
            },
            {
                'name': 'file',
                'display_name': 'File Upload',
                'description': 'Upload any file type',
                'data_type': 'file',
                'supports_options': False,
                'supports_media': True,
                'supports_geolocation': False,
            },
            {
                'name': 'signature',
                'display_name': 'Digital Signature',
                'description': 'Capture digital signature',
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
            }
        ]
    
    # Cache management
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is valid"""
        if cache_key not in self._questions_cache:
            return False
        
        cache_entry = self._questions_cache[cache_key]
        cache_age = time.time() - cache_entry['timestamp']
        return cache_age < self._cache_timeout
    
    def _cache_questions(self, cache_key: str, data: Any):
        """Cache data with timestamp"""
        self._questions_cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def _clear_cache(self, cache_key: str = None):
        """Clear cache entries"""
        if cache_key:
            self._questions_cache.pop(cache_key, None)
        else:
            self._questions_cache.clear()


# Maintain backward compatibility
FormService = ModernFormService