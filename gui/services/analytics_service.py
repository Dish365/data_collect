import json
import requests
from datetime import datetime
import pandas as pd
from typing import Dict, List, Any, Optional


class AnalyticsService:
    """Service for handling analytics operations and backend communication"""
    
    def __init__(self, auth_service, db_service):
        self.auth_service = auth_service
        self.db_service = db_service
        self.base_url = "http://127.0.0.1:8001"  # Analytics backend URL
        self.cache = {}  # Simple caching mechanism
        self.session = requests.Session()
        self._setup_session_headers()
        
    def _setup_session_headers(self):
        """Setup session headers for analytics requests"""
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'DataCollect-GUI/1.0'
        })
        
    def _make_analytics_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
        """Make authenticated request to analytics backend"""
        try:
            url = f"{self.base_url}/api/v1/analytics/{endpoint}"
            
            if method == 'GET':
                response = self.session.get(url, timeout=30)
            elif method == 'POST':
                response = self.session.post(url, json=data, timeout=60)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            if response.status_code == 200:
                result = response.json()
                # Handle the standardized response format
                if isinstance(result, dict) and 'status' in result:
                    if result['status'] == 'success':
                        return result.get('data', {})
                    else:
                        return {'error': result.get('message', 'Unknown error')}
                return result
            else:
                try:
                    error_detail = response.json()
                    return {'error': error_detail.get('detail', f'HTTP {response.status_code}')}
                except:
                    return {'error': f'HTTP {response.status_code}: {response.text}'}
                
        except requests.exceptions.ConnectionError:
            return {'error': 'Cannot connect to analytics backend. Please ensure the FastAPI server is running on port 8001.'}
        except requests.exceptions.Timeout:
            return {'error': 'Request timed out. Please try again later.'}
        except requests.exceptions.RequestException as e:
            return {'error': f'Network error: {str(e)}'}
        except Exception as e:
            return {'error': f'Request error: {str(e)}'}

    def get_project_stats(self, project_id: str) -> Dict:
        """Get basic project statistics from analytics backend"""
        cache_key = f"stats_{project_id}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_time = self.cache[cache_key].get('timestamp', 0)
            if datetime.now().timestamp() - cached_time < 300:  # 5 minutes cache
                return self.cache[cache_key]['data']
        
        try:
            result = self._make_analytics_request(f"project/{project_id}/stats")
            
            if 'error' not in result:
                # Cache successful result
                self.cache[cache_key] = {
                    'data': result,
                    'timestamp': datetime.now().timestamp()
                }
            
            return result
                
        except Exception as e:
            return {'error': f'Error getting project stats: {str(e)}'}

    def get_data_characteristics(self, project_id: str) -> Dict:
        """Get data characteristics for a project from analytics backend"""
        cache_key = f"characteristics_{project_id}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_time = self.cache[cache_key].get('timestamp', 0)
            if datetime.now().timestamp() - cached_time < 300:  # 5 minutes cache
                return self.cache[cache_key]['data']
        
        try:
            result = self._make_analytics_request(f'project/{project_id}/data-characteristics')
            
            if 'error' not in result:
                # Cache successful result
                self.cache[cache_key] = {
                    'data': result,
                    'timestamp': datetime.now().timestamp()
                }
            
            return result
            
        except Exception as e:
            return {'error': f'Error getting data characteristics: {str(e)}'}

    def get_analysis_recommendations(self, project_id: str) -> Dict:
        """Get smart analysis recommendations from analytics backend"""
        cache_key = f"recommendations_{project_id}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_time = self.cache[cache_key].get('timestamp', 0)
            if datetime.now().timestamp() - cached_time < 300:  # 5 minutes cache
                return self.cache[cache_key]['data']
        
        try:
            result = self._make_analytics_request(f'project/{project_id}/recommendations')
            
            if 'error' not in result:
                # Cache successful result
                self.cache[cache_key] = {
                    'data': result,
                    'timestamp': datetime.now().timestamp()
                }
            
            return result
            
        except Exception as e:
            return {'error': f'Error getting analysis recommendations: {str(e)}'}

    def run_analysis(self, project_id: str, analysis_type: str = "auto", analysis_config: Dict = None) -> Dict:
        """Run analysis using the analytics backend"""
        try:
            # Prepare request data
            request_data = {'analysis_type': analysis_type}
            if analysis_config:
                request_data.update(analysis_config)
            
            # Make request to backend
            result = self._make_analytics_request(f'project/{project_id}/analyze', method='POST', data=request_data)
            
            return result
            
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}

    def run_descriptive_analysis(self, project_id: str, analysis_config: Dict = None) -> Dict:
        """Run descriptive statistical analysis"""
        try:
            request_data = {'analysis_type': 'descriptive'}
            if analysis_config:
                request_data.update(analysis_config)
            
            result = self._make_analytics_request(f'project/{project_id}/analyze', method='POST', data=request_data)
            
            return result
            
        except Exception as e:
            return {'error': f'Descriptive analysis failed: {str(e)}'}

    def run_correlation_analysis(self, project_id: str, analysis_config: Dict = None) -> Dict:
        """Run correlation analysis"""
        try:
            request_data = {'analysis_type': 'correlation'}
            if analysis_config:
                request_data.update(analysis_config)
            
            result = self._make_analytics_request(f'project/{project_id}/analyze', method='POST', data=request_data)
            
            return result
            
        except Exception as e:
            return {'error': f'Correlation analysis failed: {str(e)}'}

    def run_text_analysis(self, project_id: str, analysis_config: Dict = None) -> Dict:
        """Run text analysis"""
        try:
            request_data = {'analysis_type': 'text'}
            if analysis_config:
                request_data.update(analysis_config)
            
            result = self._make_analytics_request(f'project/{project_id}/analyze', method='POST', data=request_data)
            
            return result
            
        except Exception as e:
            return {'error': f'Text analysis failed: {str(e)}'}

    def run_inferential_analysis(self, project_id: str, analysis_config: Dict) -> Dict:
        """Run inferential statistical analysis"""
        try:
            request_data = {'analysis_type': 'inferential'}
            if analysis_config:
                request_data.update(analysis_config)
            
            result = self._make_analytics_request(f'project/{project_id}/analyze', method='POST', data=request_data)
            
            return result
            
        except Exception as e:
            return {'error': f'Inferential analysis failed: {str(e)}'}

    def run_qualitative_analysis(self, project_id: str, analysis_config: Dict) -> Dict:
        """Run qualitative text analysis"""
        try:
            request_data = {'analysis_type': 'qualitative'}
            if analysis_config:
                request_data.update(analysis_config)
            
            result = self._make_analytics_request(f'project/{project_id}/analyze', method='POST', data=request_data)
            
            return result
            
        except Exception as e:
            return {'error': f'Qualitative analysis failed: {str(e)}'}

    def run_custom_analysis(self, project_id: str, data: Dict[str, Any], analysis_type: str = "auto") -> Dict:
        """Run analysis on custom data"""
        try:
            request_data = {
                'data': data,
                'analysis_type': analysis_type
            }
            
            result = self._make_analytics_request(f'project/{project_id}/analyze/custom', method='POST', data=request_data)
            
            return result
            
        except Exception as e:
            return {'error': f'Custom analysis failed: {str(e)}'}

    def check_backend_health(self) -> Dict:
        """Check if analytics backend is available"""
        try:
            result = self._make_analytics_request('health')
            return result
        except Exception as e:
            return {'error': f'Backend health check failed: {str(e)}', 'available': False}

    def export_analysis_results(self, results: Dict, format: str = 'json') -> str:
        """Export analysis results in specified format"""
        try:
            if format.lower() == 'json':
                return json.dumps(results, indent=2, default=str)
            elif format.lower() == 'csv':
                # Convert to CSV if possible
                if 'basic_statistics' in results:
                    # Create a simple CSV representation
                    csv_data = "Analysis Results\n"
                    csv_data += f"Generated: {datetime.now().isoformat()}\n\n"
                    csv_data += str(results)
                    return csv_data
                else:
                    return json.dumps(results, indent=2, default=str)
            else:
                return json.dumps(results, indent=2, default=str)
                
        except Exception as e:
            return f"Export failed: {str(e)}"

    def clear_cache(self):
        """Clear the analysis cache"""
        self.cache.clear()

    def get_cache_info(self) -> Dict:
        """Get information about cached analyses"""
        return {
            'cached_analyses': len(self.cache),
            'cache_keys': list(self.cache.keys())
        }

    def get_project_data(self, project_id: str) -> pd.DataFrame:
        """Get project data as pandas DataFrame for local use (kept for compatibility)"""
        conn = None
        try:
            conn = self.db_service.get_db_connection()
            
            # Get all responses for the project with question details
            query = """
                SELECT 
                    r.response_id,
                    r.respondent_id,
                    r.question_id,
                    r.response_value,
                    r.response_metadata,
                    r.collected_at,
                    q.question_text,
                    q.question_type,
                    q.options
                FROM responses r
                JOIN questions q ON r.question_id = q.id
                WHERE r.project_id = ?
                ORDER BY r.respondent_id, q.order_index
            """
            
            cursor = conn.cursor()
            cursor.execute(query, (project_id,))
            results = cursor.fetchall()
            
            if not results:
                return pd.DataFrame()
                
            # Convert to DataFrame
            df = pd.DataFrame([dict(row) for row in results])
            
            # Pivot to have questions as columns
            pivot_df = df.pivot_table(
                index='respondent_id',
                columns='question_text',
                values='response_value',
                aggfunc='first'
            )
            
            return pivot_df
            
        except Exception as e:
            print(f"Error getting project data: {e}")
            return pd.DataFrame()
        finally:
            if conn:
                conn.close() 