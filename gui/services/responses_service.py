import json
from datetime import datetime
import time
import urllib.parse

class ResponsesService:
    def __init__(self, auth_service, db_service, data_collection_service):
        self.auth_service = auth_service
        self.db_service = db_service
        self.data_collection_service = data_collection_service
        self.use_api_first = True  # Prefer API over local DB

    def _safe_db_read(self, db_func, *args, **kwargs):
        """Executes a database read operation with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return db_func(*args, **kwargs)
            except Exception as e:
                if 'database is locked' in str(e) and attempt < max_retries - 1:
                    time.sleep(0.1)
                else:
                    raise

    def get_all_respondents_with_responses(self, search_query=None, limit=20, offset=0):
        """Get all respondents for the current user with their response counts"""
        if self.use_api_first:
            try:
                # Try API first
                return self._get_respondents_from_api(search_query, limit, offset)
            except Exception as e:
                print(f"API failed, falling back to local DB: {e}")
                return self._get_respondents_from_db(search_query, limit, offset)
        else:
            return self._get_respondents_from_db(search_query, limit, offset)

    def _get_respondents_from_api(self, search_query=None, limit=20, offset=0):
        """Get respondents from backend API"""
        try:
            # Build API URL with pagination and search
            url = 'api/v1/respondents/with_response_counts/'
            query_params = []
            
            # Add pagination parameters
            page_size = limit
            page = (offset // limit) + 1
            query_params.append(f'page_size={page_size}')
            query_params.append(f'page={page}')
            
            # Add search query if provided
            if search_query and search_query.strip():
                # URL encode the search query
                encoded_query = urllib.parse.quote(search_query.strip())
                query_params.append(f'search={encoded_query}')
            
            # Build final URL with query parameters
            if query_params:
                url += '?' + '&'.join(query_params)
            
            response = self.auth_service.make_authenticated_request(url)
            
            if 'error' in response:
                raise Exception(response.get('message', 'API error'))
            
            # Handle paginated response
            results = response.get('results', response) if 'results' in response else response
            
            # Format data for frontend consumption
            formatted_respondents = []
            for respondent in results:
                formatted = self._format_respondent_data(respondent)
                formatted_respondents.append(formatted)
            
            return formatted_respondents, None
            
        except Exception as e:
            print(f"Error getting respondents from API: {e}")
            raise e

    def _get_respondents_from_db(self, search_query=None, limit=20, offset=0):
        """Fallback method to get respondents from local database"""
        try:
            user_data = self.auth_service.get_user_data()
            user_id = user_data.get('id') if user_data else None
            
            if not user_id:
                return [], "User not authenticated"

            def db_read():
                conn = self.db_service.get_db_connection()
                try:
                    cursor = conn.cursor()
                    
                    # Build the query with optional search
                    base_query = """
                        SELECT 
                            r.id,
                            r.respondent_id,
                            r.project_id,
                            r.name,
                            r.email,
                            r.phone,
                            r.created_at,
                            r.last_response_at,
                            r.is_anonymous,
                            p.name as project_name,
                            COUNT(resp.response_id) as response_count
                        FROM respondents r
                        LEFT JOIN projects p ON r.project_id = p.id
                        LEFT JOIN responses resp ON r.respondent_id = resp.respondent_id
                        WHERE r.user_id = ?
                    """
                    
                    params = [user_id]
                    
                    if search_query and search_query.strip():
                        base_query += """
                            AND (r.respondent_id LIKE ? OR 
                                 r.name LIKE ? OR 
                                 r.email LIKE ? OR 
                                 p.name LIKE ?)
                        """
                        search_param = f'%{search_query.strip()}%'
                        params.extend([search_param, search_param, search_param, search_param])
                    
                    base_query += """
                        GROUP BY r.id, r.respondent_id, r.project_id, r.name, r.email, r.phone, 
                                 r.created_at, r.last_response_at, r.is_anonymous, p.name
                        ORDER BY r.created_at DESC
                        LIMIT ? OFFSET ?
                    """
                    params.extend([limit, offset])
                    
                    cursor.execute(base_query, params)
                    respondents = [dict(row) for row in cursor.fetchall()]
                    
                    # Format the data using shared formatter
                    formatted_respondents = []
                    for respondent in respondents:
                        formatted = self._format_respondent_data(respondent)
                        formatted_respondents.append(formatted)
                    
                    return formatted_respondents, None
                    
                except Exception as e:
                    return [], str(e)
                finally:
                    if conn:
                        conn.close()
            
            return self._safe_db_read(db_read)
            
        except Exception as e:
            print(f"Error getting respondents from DB: {e}")
            return [], str(e)

    def _format_respondent_data(self, respondent):
        """Format respondent data for consistent frontend display"""
        try:
            # Handle different data sources (API vs DB)
            if isinstance(respondent, dict):
                # API response format
                formatted = {
                    'id': respondent.get('id'),
                    'respondent_id': respondent.get('respondent_id', ''),
                    'project_id': respondent.get('project') or respondent.get('project_id'),
                    'name': respondent.get('name', ''),
                    'email': respondent.get('email', ''),
                    'phone': respondent.get('phone', ''),
                    'created_at': respondent.get('created_at'),
                    'last_response_at': respondent.get('last_response_at'),
                    'is_anonymous': respondent.get('is_anonymous', True),
                    'response_count': respondent.get('response_count', 0),
                    'demographics': respondent.get('demographics', {})
                }
                
                # Extract project name from different possible formats
                project_details = respondent.get('project_details', {})
                if project_details:
                    formatted['project_name'] = project_details.get('name', 'Unknown Project')
                else:
                    formatted['project_name'] = respondent.get('project_name', 'Unknown Project')
            else:
                formatted = dict(respondent)
            
            # Ensure all required fields have non-None values
            formatted['respondent_id'] = formatted.get('respondent_id') or 'Unknown'
            formatted['name'] = formatted.get('name') or ''
            formatted['email'] = formatted.get('email') or ''
            formatted['phone'] = formatted.get('phone') or ''
            formatted['project_name'] = formatted.get('project_name') or 'Unknown Project'
            formatted['response_count'] = formatted.get('response_count') or 0
            
            # Parse JSON fields safely
            if formatted.get('demographics') and isinstance(formatted['demographics'], str):
                try:
                    formatted['demographics'] = json.loads(formatted['demographics'])
                except:
                    formatted['demographics'] = {}
            
            # Format dates
            for date_field in ['created_at', 'last_response_at']:
                if formatted.get(date_field):
                    try:
                        date_str = str(formatted[date_field]).replace('Z', '')
                        if '+' in date_str:
                            date_str = date_str.split('+')[0]
                        date_obj = datetime.fromisoformat(date_str)
                        formatted[f'{date_field}_formatted'] = date_obj.strftime('%Y-%m-%d %H:%M')
                    except:
                        formatted[f'{date_field}_formatted'] = str(formatted[date_field])
                else:
                    formatted[f'{date_field}_formatted'] = 'Not available'
            
            # Special handling for last_response_at
            if not formatted.get('last_response_at'):
                formatted['last_response_formatted'] = 'No responses'
            
            # Handle anonymous display
            if formatted.get('is_anonymous') or not formatted.get('name'):
                respondent_id = formatted.get('respondent_id', 'Unknown')
                if len(respondent_id) > 8:
                    formatted['display_name'] = f"Anonymous ({respondent_id[-8:]})"
                else:
                    formatted['display_name'] = f"Anonymous ({respondent_id})"
            else:
                formatted['display_name'] = formatted['name']
            
            return formatted
            
        except Exception as e:
            print(f"Error formatting respondent data: {e}")
            # Return a safe default structure
            return {
                'id': respondent.get('id', ''),
                'respondent_id': respondent.get('respondent_id', 'Unknown'),
                'project_name': 'Unknown Project',
                'display_name': 'Unknown Respondent',
                'response_count': 0,
                'created_at_formatted': 'Unknown',
                'last_response_formatted': 'No responses',
                'name': '',
                'email': '',
                'phone': ''
            }

    def get_respondent_detail_with_responses(self, respondent_id):
        """Get detailed information about a respondent and all their responses"""
        if self.use_api_first:
            try:
                return self._get_respondent_detail_from_api(respondent_id)
            except Exception as e:
                print(f"API failed for respondent detail, falling back to local DB: {e}")
                return self._get_respondent_detail_from_db(respondent_id)
        else:
            return self._get_respondent_detail_from_db(respondent_id)

    def _get_respondent_detail_from_api(self, respondent_id):
        """Get respondent details from backend API"""
        try:
            # First get the respondent by respondent_id using search
            # URL encode the respondent_id for the search query
            encoded_respondent_id = urllib.parse.quote(respondent_id)
            search_url = f'api/v1/respondents/?search={encoded_respondent_id}'
            
            response = self.auth_service.make_authenticated_request(search_url)
            
            if 'error' in response:
                raise Exception(response.get('message', 'API error'))
            
            # Handle paginated response
            results = response.get('results', response) if 'results' in response else response
            if not results:
                return None, "Respondent not found"
            
            # Find the exact match
            respondent = None
            for r in results:
                if r.get('respondent_id') == respondent_id:
                    respondent = r
                    break
            
            if not respondent:
                return None, "Respondent not found"
            
            # Get responses for this respondent
            responses_response = self.auth_service.make_authenticated_request(
                f'api/v1/respondents/{respondent["id"]}/responses/'
            )
            
            if 'error' in responses_response:
                # If we can't get responses, just return respondent info
                formatted_respondent = self._format_respondent_data(respondent)
                formatted_respondent['responses'] = []
                return formatted_respondent, None
            
            # Format the data
            formatted_respondent = self._format_respondent_data(responses_response.get('respondent', respondent))
            responses = responses_response.get('responses', [])
            
            # Format response data
            formatted_responses = []
            for response in responses:
                formatted_response = self._format_response_data(response)
                formatted_responses.append(formatted_response)
            
            formatted_respondent['responses'] = formatted_responses
            return formatted_respondent, None
            
        except Exception as e:
            print(f"Error getting respondent details from API: {e}")
            raise e

    def _get_respondent_detail_from_db(self, respondent_id):
        """Fallback method to get respondent details from local database"""
        try:
            user_data = self.auth_service.get_user_data()
            user_id = user_data.get('id') if user_data else None
            
            if not user_id:
                return None, "User not authenticated"

            def db_read():
                conn = self.db_service.get_db_connection()
                try:
                    cursor = conn.cursor()
                    
                    # Get respondent details
                    cursor.execute("""
                        SELECT 
                            r.*,
                            p.name as project_name
                        FROM respondents r
                        LEFT JOIN projects p ON r.project_id = p.id
                        WHERE r.respondent_id = ? AND r.user_id = ?
                    """, (respondent_id, user_id))
                    
                    respondent = cursor.fetchone()
                    if not respondent:
                        return None, "Respondent not found"
                    
                    respondent = dict(respondent)
                    
                    # Get all responses for this respondent
                    cursor.execute("""
                        SELECT 
                            resp.*,
                            COALESCE(q.question_text, 'Unknown Question') as question_text,
                            COALESCE(q.question_type, 'text') as question_type
                        FROM responses resp
                        LEFT JOIN questions q ON resp.question_id = q.id
                        WHERE resp.respondent_id = ?
                        ORDER BY resp.collected_at
                    """, (respondent_id,))
                    
                    responses = [dict(row) for row in cursor.fetchall()]
                    
                    # Format using shared formatters
                    formatted_respondent = self._format_respondent_data(respondent)
                    formatted_responses = []
                    for response in responses:
                        formatted_response = self._format_response_data(response)
                        formatted_responses.append(formatted_response)
                    
                    formatted_respondent['responses'] = formatted_responses
                    return formatted_respondent, None
                    
                except Exception as e:
                    return None, str(e)
                finally:
                    if conn:
                        conn.close()
            
            return self._safe_db_read(db_read)
            
        except Exception as e:
            print(f"Error getting respondent details from DB: {e}")
            return None, str(e)

    def _format_response_data(self, response):
        """Format response data for consistent display"""
        try:
            formatted = {
                'response_id': response.get('response_id', ''),
                'question_text': response.get('question_text', 'Unknown Question'),
                'question_type': response.get('question_type', 'text'),
                'response_value': response.get('response_value', 'No answer'),
                'collected_at': response.get('collected_at'),
                'response_metadata': response.get('response_metadata', {})
            }
            
            # Handle question details from API response
            question_details = response.get('question_details', {})
            if question_details:
                formatted['question_text'] = question_details.get('question_text', formatted['question_text'])
                formatted['question_type'] = question_details.get('response_type', formatted['question_type'])
            
            # Parse JSON fields safely
            if formatted.get('response_metadata') and isinstance(formatted['response_metadata'], str):
                try:
                    formatted['response_metadata'] = json.loads(formatted['response_metadata'])
                except:
                    formatted['response_metadata'] = {}
            
            # Format collection date
            if formatted.get('collected_at'):
                try:
                    date_str = str(formatted['collected_at']).replace('Z', '')
                    if '+' in date_str:
                        date_str = date_str.split('+')[0]
                    date_obj = datetime.fromisoformat(date_str)
                    formatted['collected_at_formatted'] = date_obj.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted['collected_at_formatted'] = str(formatted['collected_at'])
            else:
                formatted['collected_at_formatted'] = 'Unknown time'
            
            # Ensure safe values
            formatted['response_value'] = formatted['response_value'] or 'No answer'
            formatted['question_text'] = formatted['question_text'] or 'Unknown Question'
            
            return formatted
            
        except Exception as e:
            print(f"Error formatting response data: {e}")
            return {
                'response_id': response.get('response_id', ''),
                'question_text': 'Unknown Question',
                'response_value': 'No answer',
                'collected_at_formatted': 'Unknown time',
                'response_metadata': {}
            }

    def get_respondents_summary(self):
        """Get summary statistics for respondents"""
        if self.use_api_first:
            try:
                return self._get_summary_from_api()
            except Exception as e:
                print(f"API failed for summary, falling back to local DB: {e}")
                return self._get_summary_from_db()
        else:
            return self._get_summary_from_db()

    def _get_summary_from_api(self):
        """Get summary statistics from backend API"""
        try:
            response = self.auth_service.make_authenticated_request('api/v1/respondents/summary/')
            
            if 'error' in response:
                raise Exception(response.get('message', 'API error'))
            
            # Ensure all values are safe for display
            summary = {
                'total_respondents': response.get('total_respondents', 0),
                'total_responses': response.get('total_responses', 0),
                'avg_responses_per_respondent': response.get('avg_responses_per_respondent', 0.0)
            }
            
            return summary, None
            
        except Exception as e:
            print(f"Error getting summary from API: {e}")
            raise e

    def _get_summary_from_db(self):
        """Fallback method to get summary from local database"""
        try:
            user_data = self.auth_service.get_user_data()
            user_id = user_data.get('id') if user_data else None
            
            if not user_id:
                return {}, "User not authenticated"

            def db_read():
                conn = self.db_service.get_db_connection()
                try:
                    cursor = conn.cursor()
                    
                    # Total respondents
                    cursor.execute("SELECT COUNT(*) FROM respondents WHERE user_id = ?", (user_id,))
                    total_respondents = cursor.fetchone()[0]
                    
                    # Total responses
                    cursor.execute("""
                        SELECT COUNT(*) FROM responses resp
                        JOIN respondents r ON resp.respondent_id = r.respondent_id
                        WHERE r.user_id = ?
                    """, (user_id,))
                    total_responses = cursor.fetchone()[0]
                    
                    # Active projects with responses
                    cursor.execute("""
                        SELECT COUNT(DISTINCT r.project_id) FROM respondents r
                        WHERE r.user_id = ?
                    """, (user_id,))
                    active_projects = cursor.fetchone()[0]
                    
                    return {
                        'total_respondents': total_respondents,
                        'total_responses': total_responses,
                        'active_projects': active_projects,
                        'avg_responses_per_respondent': round(total_responses / max(total_respondents, 1), 1)
                    }, None
                    
                except Exception as e:
                    return {}, str(e)
                finally:
                    if conn:
                        conn.close()
            
            return self._safe_db_read(db_read)
            
        except Exception as e:
            print(f"Error getting summary from DB: {e}")
            return {}, str(e)

    # CRUD Operations for Respondents
    def create_respondent(self, respondent_data):
        """Create a new respondent"""
        try:
            response = self.auth_service.make_authenticated_request(
                'api/v1/respondents/',
                method='POST',
                data=respondent_data
            )
            
            if 'error' in response:
                return None, response.get('message', 'Failed to create respondent')
            
            return self._format_respondent_data(response), None
            
        except Exception as e:
            print(f"Error creating respondent: {e}")
            return None, str(e)

    def update_respondent(self, respondent_id, respondent_data):
        """Update an existing respondent"""
        try:
            response = self.auth_service.make_authenticated_request(
                f'api/v1/respondents/{respondent_id}/',
                method='PUT',
                data=respondent_data
            )
            
            if 'error' in response:
                return None, response.get('message', 'Failed to update respondent')
            
            return self._format_respondent_data(response), None
            
        except Exception as e:
            print(f"Error updating respondent: {e}")
            return None, str(e)

    def delete_respondent(self, respondent_id):
        """Delete a respondent"""
        try:
            response = self.auth_service.make_authenticated_request(
                f'api/v1/respondents/{respondent_id}/',
                method='DELETE'
            )
            
            if 'error' in response:
                return False, response.get('message', 'Failed to delete respondent')
            
            return True, None
            
        except Exception as e:
            print(f"Error deleting respondent: {e}")
            return False, str(e)

    def create_response(self, response_data):
        """Create a new response"""
        try:
            response = self.auth_service.make_authenticated_request(
                'api/v1/responses/',
                method='POST',
                data=response_data
            )
            
            if 'error' in response:
                return None, response.get('message', 'Failed to create response')
            
            return self._format_response_data(response), None
            
        except Exception as e:
            print(f"Error creating response: {e}")
            return None, str(e)

    def update_response(self, response_id, response_data):
        """Update an existing response"""
        try:
            response = self.auth_service.make_authenticated_request(
                f'api/v1/responses/{response_id}/',
                method='PUT',
                data=response_data
            )
            
            if 'error' in response:
                return None, response.get('message', 'Failed to update response')
            
            return self._format_response_data(response), None
            
        except Exception as e:
            print(f"Error updating response: {e}")
            return None, str(e)

    def delete_response(self, response_id):
        """Delete a response"""
        try:
            response = self.auth_service.make_authenticated_request(
                f'api/v1/responses/{response_id}/',
                method='DELETE'
            )
            
            if 'error' in response:
                return False, response.get('message', 'Failed to delete response')
            
            return True, None
            
        except Exception as e:
            print(f"Error deleting response: {e}")
            return False, str(e) 