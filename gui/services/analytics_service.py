import json
import requests
from datetime import datetime
import pandas as pd
from typing import Dict, List, Any, Optional


class AnalyticsService:
    """Enhanced service for handling comprehensive analytics operations and backend communication
    
    Note: Many specific analytics methods have been moved to dedicated service classes:
    - Data exploration: DataExplorationService
    - Auto detection: AutoDetectionAnalyticsHandler  
    - Descriptive analytics: DescriptiveAnalyticsHandler
    - Qualitative analytics: QualitativeAnalyticsHandler
    
    This service now primarily handles:
    - Core backend communication
    - Legacy method wrappers for backward compatibility
    - General analytics operations
    """
    
    def __init__(self, auth_service, db_service):
        self.auth_service = auth_service
        self.db_service = db_service
        self.base_url = "http://127.0.0.1:8001"  # Analytics backend URL
        self.cache = {}  # Simple caching mechanism
        self.session = requests.Session()
        self._setup_session_headers()
        self.available_analysis_types = [
            'auto', 'descriptive', 'basic', 'comprehensive', 'distribution', 
            'categorical', 'outlier', 'missing', 'temporal', 'geospatial', 
            'quality', 'correlation', 'text'
        ]
        
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
                if data:
                    response = self.session.post(url, json=data, timeout=60)
                else:
                    # POST request without JSON body (query parameters only)
                    response = self.session.post(url, timeout=60)
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
                    error_msg = error_detail.get('detail', f'HTTP {response.status_code}')
                    
                    # Enhanced error handling for validation errors
                    if response.status_code == 422 and isinstance(error_detail.get('detail'), list):
                        validation_errors = error_detail['detail']
                        error_messages = []
                        for error in validation_errors:
                            if isinstance(error, dict):
                                location = ' -> '.join(map(str, error.get('loc', [])))
                                message = error.get('msg', 'Unknown error')
                                error_messages.append(f"{location}: {message}")
                        error_msg = f"Validation error: {'; '.join(error_messages)}"
                    
                    return {'error': error_msg}
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

    # === Core Analytics Methods ===

    def get_project_stats(self, project_id: str) -> Dict:
        """Get basic project statistics from analytics backend"""
        cache_key = f"stats_{project_id}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_time = self.cache[cache_key].get('timestamp', 0)
            if datetime.now().timestamp() - cached_time < 300:  # 5 minutes cache
                return self.cache[cache_key]['data']
        
        try:
            result = self._make_analytics_request(f"auto/project/{project_id}/stats")
            
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
            result = self._make_analytics_request(f'auto/project/{project_id}/data-characteristics')
            
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
            result = self._make_analytics_request(f'auto/project/{project_id}/recommendations')
            
            if 'error' not in result:
                # Cache successful result
                self.cache[cache_key] = {
                    'data': result,
                    'timestamp': datetime.now().timestamp()
                }
            
            return result
            
        except Exception as e:
            return {'error': f'Error getting analysis recommendations: {str(e)}'}

    def get_available_analysis_types(self) -> Dict:
        """Get all available analysis types from backend"""
        try:
            result = self._make_analytics_request('auto/analysis-types')
            return result
        except Exception as e:
            return {'error': f'Error getting analysis types: {str(e)}'}

    def get_analytics_endpoints(self) -> Dict:
        """Get all available analytics endpoints"""
        try:
            result = self._make_analytics_request('auto/endpoints')
            return result
        except Exception as e:
            return {'error': f'Error getting endpoints: {str(e)}'}

    # === Comprehensive Analysis Methods ===

    def run_analysis(self, project_id: str, analysis_type: str = "auto", 
                    target_variables: Optional[List[str]] = None) -> Dict:
        """Run comprehensive analysis using the analytics backend"""
        try:
            # Send as query parameters only - no JSON body
            import urllib.parse
            
            params = [('analysis_type', analysis_type)]
            if target_variables and isinstance(target_variables, list):
                for var in target_variables:
                    params.append(('target_variables', var))
            elif target_variables:
                params.append(('target_variables', target_variables))
            
            url = f"auto/project/{project_id}/analyze"
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            # Make POST request with no body (query parameters only)
            result = self._make_analytics_request(url, method='POST')
            
            return result
            
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}

    def run_basic_statistics(self, project_id: str, variables: Optional[List[str]] = None) -> Dict:
        """Run basic statistical analysis"""
        try:
            import urllib.parse
            
            params = []
            if variables and isinstance(variables, list):
                for var in variables:
                    params.append(('variables', var))
            elif variables:
                params.append(('variables', variables))
            
            url = f'descriptive/project/{project_id}/analyze/basic-statistics'
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            result = self._make_analytics_request(url, method='POST')
            return result
            
        except Exception as e:
            return {'error': f'Basic statistics failed: {str(e)}'}

    def run_distribution_analysis(self, project_id: str, variables: Optional[List[str]] = None) -> Dict:
        """Run distribution analysis"""
        try:
            import urllib.parse
            
            params = []
            if variables and isinstance(variables, list):
                for var in variables:
                    params.append(('variables', var))
            elif variables:
                params.append(('variables', variables))
            
            url = f'descriptive/project/{project_id}/analyze/distributions'
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            result = self._make_analytics_request(url, method='POST')
            return result
            
        except Exception as e:
            return {'error': f'Distribution analysis failed: {str(e)}'}

    def run_categorical_analysis(self, project_id: str, variables: Optional[List[str]] = None) -> Dict:
        """Run categorical analysis"""
        try:
            import urllib.parse
            
            params = []
            if variables and isinstance(variables, list):
                for var in variables:
                    params.append(('variables', var))
            elif variables:
                params.append(('variables', variables))
            
            url = f'descriptive/project/{project_id}/analyze/categorical'
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            result = self._make_analytics_request(url, method='POST')
            return result
            
        except Exception as e:
            return {'error': f'Categorical analysis failed: {str(e)}'}

    def run_outlier_analysis(self, project_id: str, variables: Optional[List[str]] = None, 
                           methods: Optional[List[str]] = None) -> Dict:
        """Run outlier detection analysis"""
        try:
            request_data = {}
            if variables:
                request_data['variables'] = variables
            if methods:
                request_data['methods'] = methods
            
            result = self._make_analytics_request(f'descriptive/project/{project_id}/analyze/outliers', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Outlier analysis failed: {str(e)}'}

    def run_missing_data_analysis(self, project_id: str) -> Dict:
        """Run missing data analysis"""
        try:
            result = self._make_analytics_request(f'descriptive/project/{project_id}/analyze/missing-data', 
                                                method='POST')
            return result
            
        except Exception as e:
            return {'error': f'Missing data analysis failed: {str(e)}'}

    def run_data_quality_analysis(self, project_id: str) -> Dict:
        """Run data quality analysis"""
        try:
            result = self._make_analytics_request(f'descriptive/project/{project_id}/analyze/data-quality', 
                                                method='POST')
            return result
            
        except Exception as e:
            return {'error': f'Data quality analysis failed: {str(e)}'}

    def run_temporal_analysis(self, project_id: str, date_column: str, 
                            value_columns: Optional[List[str]] = None) -> Dict:
        """Run temporal analysis"""
        try:
            request_data = {'date_column': date_column}
            if value_columns:
                request_data['value_columns'] = value_columns
            
            result = self._make_analytics_request(f'descriptive/project/{project_id}/analyze/temporal', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Temporal analysis failed: {str(e)}'}

    def run_geospatial_analysis(self, project_id: str, lat_column: str, lon_column: str) -> Dict:
        """Run geospatial analysis"""
        try:
            request_data = {'lat_column': lat_column, 'lon_column': lon_column}
            
            result = self._make_analytics_request(f'descriptive/project/{project_id}/analyze/geospatial', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Geospatial analysis failed: {str(e)}'}

    def generate_comprehensive_report(self, project_id: str, include_plots: bool = False) -> Dict:
        """Generate comprehensive analytics report"""
        try:
            request_data = {'include_plots': include_plots}
            
            result = self._make_analytics_request(f'descriptive/project/{project_id}/generate-report', 
                                                method='POST', data=request_data)
            return result
            
        except Exception as e:
            return {'error': f'Report generation failed: {str(e)}'}

    # === Legacy Methods for Backward Compatibility ===

    def run_descriptive_analysis(self, project_id: str, analysis_config: Dict = None) -> Dict:
        """Run descriptive statistical analysis (legacy wrapper)"""
        try:
            target_variables = None
            if analysis_config and 'variables' in analysis_config:
                target_variables = analysis_config['variables']
            
            return self.run_analysis(project_id, "descriptive", target_variables)
            
        except Exception as e:
            return {'error': f'Descriptive analysis failed: {str(e)}'}

    def run_correlation_analysis(self, project_id: str, analysis_config: Dict = None) -> Dict:
        """Run correlation analysis (legacy wrapper)"""
        try:
            target_variables = None
            if analysis_config and 'variables' in analysis_config:
                target_variables = analysis_config['variables']
            
            return self.run_analysis(project_id, "correlation", target_variables)
            
        except Exception as e:
            return {'error': f'Correlation analysis failed: {str(e)}'}

    def run_text_analysis(self, project_id: str, analysis_config: Dict = None) -> Dict:
        """Run text analysis (legacy wrapper)"""
        try:
            target_variables = None
            if analysis_config and 'variables' in analysis_config:
                target_variables = analysis_config['variables']
            
            return self.run_analysis(project_id, "text", target_variables)
            
        except Exception as e:
            return {'error': f'Text analysis failed: {str(e)}'}

    def run_inferential_analysis(self, project_id: str, analysis_config: Dict) -> Dict:
        """Run inferential statistical analysis"""
        try:
            request_data = {'analysis_type': 'inferential'}
            if analysis_config:
                request_data.update(analysis_config)
            
            result = self._make_analytics_request(f'inferential/project/{project_id}/analyze/correlation', method='POST', data=request_data)
            
            return result
            
        except Exception as e:
            return {'error': f'Inferential analysis failed: {str(e)}'}

    def run_qualitative_analysis(self, project_id: str, analysis_config: Dict) -> Dict:
        """Run qualitative text analysis"""
        try:
            target_variables = None
            if analysis_config and 'variables' in analysis_config:
                target_variables = analysis_config['variables']
            
            # Use the qualitative endpoints for text analysis
            import urllib.parse
            params = []
            if target_variables and isinstance(target_variables, list):
                for var in target_variables:
                    params.append(('text_fields', var))
            elif target_variables:
                params.append(('text_fields', target_variables))
            
            url = f"qualitative/project/{project_id}/analyze/text"
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            result = self._make_analytics_request(url, method='POST')
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
            
            result = self._make_analytics_request(f'descriptive/project/{project_id}/analyze/custom', method='POST', data=request_data)
            
            return result
            
        except Exception as e:
            return {'error': f'Custom analysis failed: {str(e)}'}

    # === Data Selection Methods ===

    def get_project_variables(self, project_id: str) -> Dict:
        """Get available variables for a project"""
        try:
            characteristics = self.get_data_characteristics(project_id)
            if 'error' in characteristics:
                return characteristics
            
            # Extract characteristics data
            char_data = characteristics.get('characteristics', characteristics)
            
            variables = {
                'all_variables': [],
                'numeric_variables': char_data.get('numeric_variables', []),
                'categorical_variables': char_data.get('categorical_variables', []),
                'text_variables': char_data.get('text_variables', []),
                'datetime_variables': char_data.get('datetime_variables', []),
                'variable_count': char_data.get('variable_count', 0),
                'sample_size': char_data.get('sample_size', 0),
                'sample_size_analysis': char_data.get('sample_size_analysis', {})
            }
            
            # Combine all variables
            variables['all_variables'] = (
                variables['numeric_variables'] + 
                variables['categorical_variables'] + 
                variables['text_variables'] + 
                variables['datetime_variables']
            )
            
            return variables
            
        except Exception as e:
            return {'error': f'Error getting project variables: {str(e)}'}

    def get_variable_details(self, project_id: str, variable_name: str) -> Dict:
        """Get detailed information about a specific variable"""
        try:
            # This would require additional backend endpoint
            # For now, return basic info from characteristics
            characteristics = self.get_data_characteristics(project_id)
            if 'error' in characteristics:
                return characteristics
            
            char_data = characteristics.get('characteristics', characteristics)
            
            # Determine variable type
            variable_type = 'unknown'
            if variable_name in char_data.get('numeric_variables', []):
                variable_type = 'numeric'
            elif variable_name in char_data.get('categorical_variables', []):
                variable_type = 'categorical'
            elif variable_name in char_data.get('text_variables', []):
                variable_type = 'text'
            elif variable_name in char_data.get('datetime_variables', []):
                variable_type = 'datetime'
            
            return {
                'variable_name': variable_name,
                'variable_type': variable_type,
                'sample_size': char_data.get('sample_size', 0)
            }
            
        except Exception as e:
            return {'error': f'Error getting variable details: {str(e)}'}

    # === Utility Methods ===

    # === Data Exploration Methods ===

    def explore_project_data(self, project_id: str, page: int = 1, page_size: int = 50, 
                           search: str = None, question_filter: str = None,
                           respondent_filter: str = None, date_from: str = None, 
                           date_to: str = None) -> Dict:
        """Explore project data with filtering and pagination"""
        try:
            import urllib.parse
            
            params = [('page', str(page)), ('page_size', str(page_size))]
            if search:
                params.append(('search', search))
            if question_filter:
                params.append(('question_filter', question_filter))
            if respondent_filter:
                params.append(('respondent_filter', respondent_filter))
            if date_from:
                params.append(('date_from', date_from))
            if date_to:
                params.append(('date_to', date_to))
            
            url = f'descriptive/project/{project_id}/explore-data'
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            result = self._make_analytics_request(url, method='GET')
            return result
            
        except Exception as e:
            return {'error': f'Data exploration failed: {str(e)}'}

    def get_data_summary(self, project_id: str) -> Dict:
        """Get quick data summary with types and samples"""
        try:
            result = self._make_analytics_request(f'descriptive/project/{project_id}/data-summary')
            return result
            
        except Exception as e:
            return {'error': f'Data summary failed: {str(e)}'}

    def check_backend_health(self) -> Dict:
        """Check if analytics backend is available"""
        try:
            result = self._make_analytics_request('auto/health')
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
                    q.response_type,
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