import json
import requests
from datetime import datetime
import pandas as pd
from typing import Dict


class AnalyticsService:
    """Service for handling analytics operations and backend communication"""
    
    def __init__(self, auth_service, db_service):
        self.auth_service = auth_service
        self.db_service = db_service
        self.base_url = "http://127.0.0.1:8001"  # Analytics backend URL
        self.cache = {}  # Simple caching mechanism
        self.backend_available = None  # Cache backend availability
        
    def _make_analytics_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
        """Make authenticated request to analytics backend"""
        try:
            url = f"{self.base_url}/api/v1/analytics/{endpoint}"
            
            headers = {'Content-Type': 'application/json'}
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=60)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            if response.status_code == 200:
                result = response.json()
                # Handle the new response format
                if isinstance(result, dict) and 'data' in result:
                    return result['data']
                return result
            else:
                return {
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'status_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {'error': f'Network error: {str(e)}'}
        except Exception as e:
            return {'error': f'Request error: {str(e)}'}

    def get_project_data(self, project_id: str) -> pd.DataFrame:
        """Get project data as pandas DataFrame for analysis with comprehensive error handling"""
        conn = None
        try:
            conn = self.db_service.get_db_connection()
            if not conn:
                print("Database connection failed")
                return pd.DataFrame()
                
            cursor = conn.cursor()
            
            # Get current user for filtering
            user_data = self.auth_service.get_user_data()
            user_id = user_data.get('id') if user_data else None
            
            if not user_id:
                print("No user_id available for analytics data filtering")
                return pd.DataFrame()
            
            # Verify project exists and has responses
            cursor.execute("""
                SELECT p.name, COUNT(r.response_id) as response_count
                FROM projects p
                LEFT JOIN responses r ON p.id = r.project_id AND r.user_id = ?
                WHERE p.id = ? AND p.user_id = ?
                GROUP BY p.id, p.name
            """, (user_id, project_id, user_id))
            project_info = cursor.fetchone()
            
            if not project_info:
                print(f"Project {project_id} not found for user {user_id}")
                return pd.DataFrame()
                
            response_count = project_info['response_count'] or 0
            print(f"Getting data for project: {project_info['name']} ({response_count} responses, user: {user_id})")
            
            if response_count == 0:
                print(f"No responses found for project {project_id}")
                return pd.DataFrame()
            
            # Get comprehensive response and question data using correct field names
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
                    q.options,
                    q.order_index,
                    CASE 
                        WHEN r.response_value IS NULL OR r.response_value = '' THEN 0 
                        ELSE 1 
                    END as has_response
                FROM responses r
                JOIN questions q ON r.question_id = q.id AND r.user_id = q.user_id
                WHERE r.project_id = ? AND r.user_id = ?
                ORDER BY r.respondent_id, q.order_index
            """
            
            cursor.execute(query, (project_id, user_id))
            results = cursor.fetchall()
            
            print(f"Found {len(results)} response records for project {project_id}")
            
            if not results:
                return pd.DataFrame()
                
            # Convert to DataFrame with enhanced data processing
            df = pd.DataFrame([dict(row) for row in results])
            
            print(f"Raw DataFrame shape: {df.shape}")
            print(f"Unique respondents: {df['respondent_id'].nunique()}")
            print(f"Unique questions: {df['question_text'].nunique()}")
            print(f"Response coverage: {df['has_response'].sum()}/{len(df)} ({(df['has_response'].sum()/len(df)*100):.1f}%)")
            
            # Create enhanced pivot table with better error handling
            try:
                pivot_df = df.pivot_table(
                    index='respondent_id',
                    columns='question_text',
                    values='response_value',
                    aggfunc='first',
                    fill_value=''  # Fill missing values with empty string
                )
                
                print(f"Pivot DataFrame shape: {pivot_df.shape}")
                print(f"Pivot DataFrame columns: {len(pivot_df.columns)}")
                
                # Add metadata for analytics
                pivot_df.attrs = {
                    'project_id': project_id,
                    'project_name': project_info['name'],
                    'total_responses': len(results),
                    'unique_respondents': df['respondent_id'].nunique(),
                    'unique_questions': df['question_text'].nunique(),
                    'response_coverage': df['has_response'].sum(),
                    'data_quality': (df['has_response'].sum()/len(df)*100) if len(df) > 0 else 0
                }
                
                return pivot_df
                
            except Exception as pivot_error:
                print(f"Error creating pivot table: {pivot_error}")
                # Return enhanced raw data if pivot fails
                df.attrs = {
                    'project_id': project_id,
                    'project_name': project_info['name'],
                    'total_responses': len(results),
                    'is_pivot_failed': True
                }
                return df
            
        except Exception as e:
            print(f"Error getting project data: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
        finally:
            if conn:
                conn.close()

    def get_project_response_data(self, project_id: str) -> Dict:
        """Get detailed response data for a project with user filtering"""
        try:
            user_data = self.auth_service.get_user_data()
            user_id = user_data.get('id') if user_data else None
            
            if not user_id:
                return {'error': 'User not authenticated'}
            
            conn = self.db_service.get_db_connection()
            cursor = conn.cursor()
            
            # Get project info
            cursor.execute("SELECT name FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
            project = cursor.fetchone()
            if not project:
                return {'error': f'Project {project_id} not found for user {user_id}'}
            
            # Get all responses with question details (user-filtered) using correct field names
            cursor.execute("""
                SELECT 
                    r.response_id,
                    r.respondent_id,
                    r.question_id,
                    r.response_value,
                    r.response_metadata,
                    r.collected_at,
                    q.question_text,
                    q.question_type,
                    q.options,
                    q.order_index
                FROM responses r
                JOIN questions q ON r.question_id = q.id
                WHERE r.project_id = ? AND r.user_id = ?
                ORDER BY r.respondent_id, q.order_index
            """, (project_id, user_id))
            
            responses = [dict(row) for row in cursor.fetchall()]
            
            # Get respondent count
            cursor.execute("""
                SELECT COUNT(DISTINCT respondent_id) as respondent_count
                FROM responses 
                WHERE project_id = ? AND user_id = ?
            """, (project_id, user_id))
            respondent_count = cursor.fetchone()['respondent_count']
            
            # Get question count
            cursor.execute("""
                SELECT COUNT(*) as question_count
                FROM questions 
                WHERE project_id = ? AND user_id = ?
            """, (project_id, user_id))
            question_count = cursor.fetchone()['question_count']
            
            return {
                'project_name': project['name'],
                'project_id': project_id,
                'user_id': user_id,
                'responses': responses,
                'total_responses': len(responses),
                'unique_respondents': respondent_count,
                'total_questions': question_count,
                'data_available': len(responses) > 0
            }
            
        except Exception as e:
            print(f"Error getting project response data: {e}")
            return {'error': str(e)}
        finally:
            if 'conn' in locals():
                conn.close()

    def get_data_characteristics(self, project_id: str) -> Dict:
        """Get data characteristics for a project with user filtering"""
        try:
            response_data = self.get_project_response_data(project_id)
            
            if 'error' in response_data:
                return response_data
            
            if not response_data.get('data_available'):
                return {
                    'project_id': project_id,
                    'observations': 0,
                    'variables': 0,
                    'message': 'No data available for analysis'
                }
            
            responses = response_data['responses']
            
            # Basic characteristics
            characteristics = {
                'project_id': project_id,
                'project_name': response_data['project_name'],
                'observations': response_data['unique_respondents'],
                'variables': response_data['total_questions'],
                'total_responses': response_data['total_responses'],
                'data_types': {},
                'completeness': 0
            }
            
            # Analyze data types and completeness
            if responses:
                # Group responses by question
                question_data = {}
                for response in responses:
                    question_id = response['question_id']
                    if question_id not in question_data:
                        question_data[question_id] = {
                            'question_text': response['question_text'],
                            'question_type': response['question_type'],
                            'responses': []
                        }
                    question_data[question_id]['responses'].append(response['response_value'])
                
                # Calculate completeness
                total_expected = response_data['unique_respondents'] * response_data['total_questions']
                actual_responses = len([r for r in responses if r['response_value'] and r['response_value'].strip()])
                characteristics['completeness'] = round((actual_responses / total_expected * 100) if total_expected > 0 else 0, 1)
                
                # Analyze data types
                for question_id, data in question_data.items():
                    question_text = data['question_text']
                    question_type = data['question_type']
                    values = [v for v in data['responses'] if v and str(v).strip()]
                    
                    characteristics['data_types'][question_text] = {
                        'type': question_type,
                        'non_empty_count': len(values),
                        'unique_values': len(set(values)) if values else 0
                    }
            
            return characteristics
            
        except Exception as e:
            print(f"Error getting data characteristics: {e}")
            return {'error': str(e)}

    def get_analysis_recommendations(self, project_id: str) -> Dict:
        """Get smart analysis recommendations from streamlined API"""
        cache_key = f"recommendations_{project_id}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_time = self.cache[cache_key].get('timestamp', 0)
            if datetime.now().timestamp() - cached_time < 300:  # 5 minutes cache
                return self.cache[cache_key]['data']
        
        try:
            # Check if backend is available first
            if self.is_backend_available():
                # Call streamlined recommendations API
                result = self._make_analytics_request(f'project/{project_id}/recommendations')
                
                if result is not None and 'error' not in result:
                    # Extract data from API response format
                    if result.get('status') == 'success':
                        api_data = result.get('data', {})
                        recommendations = api_data.get('recommendations', [])
                        
                        # Cache the results
                        self.cache[cache_key] = {
                            'data': recommendations,
                            'timestamp': datetime.now().timestamp()
                        }
                        
                        return recommendations
            
            # Fallback to local recommendations if backend fails or unavailable
            print(f"Analytics backend unavailable, using local recommendations for project {project_id}")
            characteristics = self.get_data_characteristics(project_id)
            return self._generate_local_recommendations(characteristics)
            
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            # Fallback to local recommendations
            characteristics = self.get_data_characteristics(project_id)
            return self._generate_local_recommendations(characteristics)

    def _generate_local_recommendations(self, characteristics: Dict) -> Dict:
        """Generate local analysis recommendations when backend is unavailable"""
        recommendations = {
            'primary_recommendations': [],
            'secondary_recommendations': [],
            'data_quality_warnings': []
        }
        
        if characteristics.get('sample_size', 0) > 0:
            # Basic statistics always recommended
            recommendations['primary_recommendations'].append({
                'method': 'basic_statistics',
                'score': 0.9,
                'rationale': f"Basic statistics suitable for {characteristics['sample_size']} responses",
                'function_call': 'run_descriptive_analysis()',
                'category': 'descriptive'
            })
            
            # Conditional recommendations based on data characteristics
            if len(characteristics.get('numeric_variables', [])) >= 2:
                recommendations['primary_recommendations'].append({
                    'method': 'correlation_analysis',
                    'score': 0.85,
                    'rationale': f"Correlation analysis for {len(characteristics['numeric_variables'])} numeric variables",
                    'function_call': 'run_correlation_analysis()',
                    'category': 'descriptive'
                })
                
            if len(characteristics.get('categorical_variables', [])) >= 1:
                recommendations['secondary_recommendations'].append({
                    'method': 'categorical_analysis',
                    'score': 0.75,
                    'rationale': f"Categorical analysis for {len(characteristics['categorical_variables'])} categorical variables",
                    'function_call': 'run_categorical_analysis()',
                    'category': 'descriptive'
                })
                
            if len(characteristics.get('text_variables', [])) >= 1:
                recommendations['secondary_recommendations'].append({
                    'method': 'sentiment_analysis',
                    'score': 0.8,
                    'rationale': f"Text analysis for {len(characteristics['text_variables'])} text fields",
                    'function_call': 'run_sentiment_analysis()',
                    'category': 'qualitative'
                })
        
        # Data quality warnings
        if characteristics.get('data_quality', {}).get('missing_data_percentage', 0) > 20:
            recommendations['data_quality_warnings'].append(
                f"High missing data rate: {characteristics['data_quality']['missing_data_percentage']:.1f}%"
            )
            
        return recommendations

    def run_descriptive_analysis(self, project_id: str, analysis_config: Dict = None) -> Dict:
        """Run descriptive statistical analysis using streamlined API"""
        try:
            # Try backend API first with correct parameter format
            result = self._make_analytics_request(f'project/{project_id}/analyze?analysis_type=descriptive', method='POST')
            
            if result is not None and 'error' not in result:
                return result
                
            # Fallback to local analysis
            df = self.get_project_data(project_id)
            if df.empty:
                return {'error': 'No data available for analysis'}
            return self._run_local_descriptive_analysis(df)
            
        except Exception as e:
            return {'error': f'Descriptive analysis failed: {str(e)}'}

    def _run_local_descriptive_analysis(self, df: pd.DataFrame) -> Dict:
        """Run local descriptive analysis when backend is unavailable"""
        try:
            if df.empty:
                return {
                    'error': 'No data available for analysis',
                    'summary': {
                        'total_responses': 0,
                        'total_variables': 0,
                        'completeness': 0
                    }
                }
            
            # Calculate completeness safely
            total_cells = df.shape[0] * df.shape[1]
            missing_cells = df.isnull().sum().sum()
            completeness = (1 - missing_cells / total_cells) * 100 if total_cells > 0 else 0
            
            results = {
                'basic_statistics': {},
                'summary': {
                    'total_responses': len(df),
                    'total_variables': len(df.columns),
                    'completeness': completeness,
                    'missing_values': int(missing_cells),
                    'data_types': {}
                }
            }
            
            # Analyze data types
            for col in df.columns:
                dtype = str(df[col].dtype)
                non_null_count = df[col].count()
                results['summary']['data_types'][col] = {
                    'type': dtype,
                    'non_null_count': int(non_null_count),
                    'null_count': int(len(df) - non_null_count)
                }
            
            # Basic statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                results['basic_statistics']['numeric'] = {}
                for col in numeric_cols:
                    if df[col].count() > 0:  # Only analyze if there's data
                        stats = df[col].describe()
                        results['basic_statistics']['numeric'][col] = {
                            'count': int(stats['count']),
                            'mean': float(stats['mean']),
                            'std': float(stats['std']),
                            'min': float(stats['min']),
                            'max': float(stats['max']),
                            'median': float(stats['50%'])
                        }
                
            # Frequency analysis for categorical columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                results['basic_statistics']['categorical'] = {}
                for col in categorical_cols:
                    if df[col].count() > 0:  # Only analyze if there's data
                        value_counts = df[col].value_counts().head(10)
                        results['basic_statistics']['categorical'][col] = {
                            'total_responses': int(df[col].count()),
                            'unique_values': int(df[col].nunique()),
                            'top_values': value_counts.to_dict()
                        }
                    
            return results
            
        except Exception as e:
            print(f"Local descriptive analysis error: {e}")
            import traceback
            traceback.print_exc()
            return {'error': f'Local descriptive analysis failed: {str(e)}'}

    def run_inferential_analysis(self, project_id: str, analysis_config: Dict = None) -> Dict:
        """Run inferential statistical analysis"""
        try:
            # Try backend API first with correct parameter format
            result = self._make_analytics_request(f'project/{project_id}/analyze?analysis_type=inferential', method='POST')
            
            if result is None or 'error' in result:
                return {'error': 'Inferential analysis not available offline'}
                
            return result
            
        except Exception as e:
            return {'error': f'Inferential analysis failed: {str(e)}'}

    def run_qualitative_analysis(self, project_id: str, analysis_config: Dict = None) -> Dict:
        """Run qualitative text analysis"""
        try:
            # Try backend API first with correct parameter format
            result = self._make_analytics_request(f'project/{project_id}/analyze?analysis_type=qualitative', method='POST')
            
            if result is None or 'error' in result:
                return self._run_local_qualitative_analysis(project_id, analysis_config or {})
                
            return result
            
        except Exception as e:
            return {'error': f'Qualitative analysis failed: {str(e)}'}

    def _run_local_qualitative_analysis(self, project_id: str, config: Dict) -> Dict:
        """Run basic local qualitative analysis"""
        try:
            df = self.get_project_data(project_id)
            
            if df.empty:
                return {'error': 'No data available'}
                
            # Simple text analysis for text columns
            text_cols = df.select_dtypes(include=['object']).columns
            results = {
                'text_analysis': {},
                'summary': {
                    'text_fields_analyzed': len(text_cols),
                    'total_text_entries': 0
                }
            }
            
            for col in text_cols:
                text_data = df[col].dropna()
                if len(text_data) > 0:
                    results['text_analysis'][col] = {
                        'total_entries': len(text_data),
                        'average_length': text_data.str.len().mean(),
                        'word_count': text_data.str.split().str.len().sum(),
                        'common_words': []  # Would need NLP library for proper analysis
                    }
                    results['summary']['total_text_entries'] += len(text_data)
                    
            return results
            
        except Exception as e:
            return {'error': f'Local qualitative analysis failed: {str(e)}'}

    def check_backend_health(self) -> Dict:
        """Check if analytics backend is available"""
        try:
            result = self._make_analytics_request('health')
            # Ensure we always return a valid dictionary
            if result is None:
                self.backend_available = False
                return {'error': 'No response from backend', 'available': False}
            
            # Check if the result indicates success
            if result.get('status') == 'success' or result.get('service') == 'analytics':
                self.backend_available = True
                return {'available': True, 'status': 'healthy', 'backend_data': result}
            else:
                self.backend_available = False
                return {'error': 'Backend unhealthy', 'available': False, 'backend_data': result}
                
        except Exception as e:
            self.backend_available = False
            return {'error': f'Backend health check failed: {str(e)}', 'available': False}
    
    def is_backend_available(self) -> bool:
        """Quick check if backend is available"""
        if self.backend_available is None:
            health = self.check_backend_health()
            return health.get('available', False)
        return self.backend_available

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

    def validate_project_for_analysis(self, project_id: str) -> Dict:
        """Comprehensive validation of project data for analysis"""
        validation_result = {
            'is_valid': False,
            'warnings': [],
            'errors': [],
            'recommendations': [],
            'data_summary': {},
            'available_analyses': []
        }
        
        try:
            # Check if project exists and has data
            response_data = self.get_project_response_data(project_id)
            
            if 'error' in response_data:
                validation_result['errors'].append(f"Project access error: {response_data['error']}")
                return validation_result
                
            total_responses = response_data.get('total_responses', 0)
            unique_respondents = response_data.get('unique_respondents', 0) 
            total_questions = response_data.get('total_questions', 0)
            
            # Basic data summary
            validation_result['data_summary'] = {
                'project_name': response_data.get('project_name', 'Unknown'),
                'total_responses': total_responses,
                'unique_respondents': unique_respondents,
                'total_questions': total_questions,
                'expected_responses': unique_respondents * total_questions,
                'completion_rate': (total_responses / (unique_respondents * total_questions) * 100) if (unique_respondents * total_questions) > 0 else 0
            }
            
            # Validation checks
            if total_responses == 0:
                validation_result['errors'].append("No responses collected yet. Please collect some data before running analysis.")
                validation_result['recommendations'].append("Go to Data Collection tab and start collecting responses for this project.")
                return validation_result
                
            if unique_respondents == 0:
                validation_result['errors'].append("No respondents found. Data collection may have failed.")
                return validation_result
                
            if total_questions == 0:
                validation_result['errors'].append("No questions found for this project.")
                validation_result['recommendations'].append("Add questions to your project in the Form Builder.")
                return validation_result
            
            # Data quality checks
            completion_rate = validation_result['data_summary']['completion_rate']
            
            if completion_rate < 50:
                validation_result['warnings'].append(f"Low completion rate ({completion_rate:.1f}%). Some analyses may be limited.")
            elif completion_rate < 80:
                validation_result['warnings'].append(f"Moderate completion rate ({completion_rate:.1f}%). Consider collecting more complete responses.")
                
            if unique_respondents < 3:
                validation_result['warnings'].append(f"Very small sample size ({unique_respondents} respondents). Statistical analyses may not be reliable.")
            elif unique_respondents < 10:
                validation_result['warnings'].append(f"Small sample size ({unique_respondents} respondents). Some statistical tests may have limited power.")
                
            # Determine available analyses
            available_analyses = ['descriptive']  # Always available if we have data
            
            if unique_respondents >= 2:
                available_analyses.append('correlation')
                
            if unique_respondents >= 5:
                available_analyses.append('inferential')
                
            # Check for text data
            responses = response_data.get('responses', [])
            has_text_data = any(
                response.get('question_type') in ['text', 'textarea', 'open_ended'] 
                for response in responses
            )
            
            if has_text_data:
                available_analyses.append('qualitative')
                
            validation_result['available_analyses'] = available_analyses
            
            # Backend availability check
            backend_health = self.check_backend_health()
            if not backend_health.get('available', False):
                validation_result['warnings'].append("Analytics backend is offline. Using local analysis capabilities.")
                validation_result['recommendations'].append("For advanced analytics, ensure the analytics backend is running.")
                
            # Final validation
            if len(validation_result['errors']) == 0:
                validation_result['is_valid'] = True
                validation_result['recommendations'].append(f"Data looks good! You can run {len(available_analyses)} types of analysis.")
                
            return validation_result
            
        except Exception as e:
            validation_result['errors'].append(f"Validation failed: {str(e)}")
            return validation_result

    def get_analysis_status_info(self, project_id: str) -> Dict:
        """Get comprehensive status information for analysis UI"""
        try:
            validation = self.validate_project_for_analysis(project_id)
            backend_health = self.check_backend_health()
            
            status_info = {
                'validation': validation,
                'backend': {
                    'available': backend_health.get('available', False),
                    'status': backend_health.get('status', 'unknown'),
                    'error': backend_health.get('error', None)
                },
                'capabilities': {
                    'local_analysis': True,
                    'backend_analysis': backend_health.get('available', False),
                    'export_formats': ['JSON', 'CSV', 'Summary']
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return status_info
            
        except Exception as e:
            return {
                'validation': {'is_valid': False, 'errors': [f"Status check failed: {str(e)}"]},
                'backend': {'available': False, 'error': str(e)},
                'capabilities': {'local_analysis': True, 'backend_analysis': False},
                'timestamp': datetime.now().isoformat()
            }

    def format_analysis_results_for_ui(self, results: Dict, analysis_type: str) -> Dict:
        """Format analysis results for optimal UI display"""
        try:
            formatted_results = {
                'analysis_type': analysis_type,
                'timestamp': datetime.now().isoformat(),
                'summary': {},
                'sections': [],
                'export_data': results,
                'ui_components': []
            }
            
            if 'error' in results:
                formatted_results['error'] = results['error']
                formatted_results['ui_components'].append({
                    'type': 'error_card',
                    'title': 'Analysis Error',
                    'message': results['error'],
                    'icon': 'alert-circle'
                })
                return formatted_results
                
            # Format based on analysis type
            if analysis_type == 'descriptive':
                return self._format_descriptive_results(results, formatted_results)
            elif analysis_type == 'inferential':
                return self._format_inferential_results(results, formatted_results)
            elif analysis_type == 'qualitative':
                return self._format_qualitative_results(results, formatted_results)
            elif analysis_type == 'auto_detection':
                return self._format_recommendations_results(results, formatted_results)
            else:
                formatted_results['sections'].append({
                    'title': f'{analysis_type.title()} Results',
                    'content': str(results)
                })
                
            return formatted_results
            
        except Exception as e:
            return {
                'analysis_type': analysis_type,
                'error': f"Result formatting failed: {str(e)}",
                'timestamp': datetime.now().isoformat(),
                'ui_components': [{
                    'type': 'error_card',
                    'title': 'Formatting Error',
                    'message': f"Could not format results: {str(e)}",
                    'icon': 'alert-circle'
                }]
            }

    def _format_descriptive_results(self, results: Dict, formatted_results: Dict) -> Dict:
        """Format descriptive analysis results for UI"""
        summary_data = results.get('summary', {})
        basic_stats = results.get('basic_statistics', {})
        
        # Summary section
        formatted_results['summary'] = {
            'total_responses': summary_data.get('total_responses', 0),
            'total_variables': summary_data.get('total_variables', 0),
            'completeness': summary_data.get('completeness', 0),
            'data_quality': 'Good' if summary_data.get('completeness', 0) > 80 else 'Fair' if summary_data.get('completeness', 0) > 50 else 'Poor'
        }
        
        # Summary card
        formatted_results['ui_components'].append({
            'type': 'summary_card',
            'title': 'Analysis Summary',
            'metrics': [
                {'label': 'Total Responses', 'value': summary_data.get('total_responses', 0), 'icon': 'database'},
                {'label': 'Variables Analyzed', 'value': summary_data.get('total_variables', 0), 'icon': 'chart-line'},
                {'label': 'Data Completeness', 'value': f"{summary_data.get('completeness', 0):.1f}%", 'icon': 'check-circle'},
                {'label': 'Data Quality', 'value': formatted_results['summary']['data_quality'], 'icon': 'shield-check'}
            ]
        })
        
        # Numeric statistics
        numeric_stats = basic_stats.get('numeric', {})
        if numeric_stats:
            for var_name, stats in numeric_stats.items():
                formatted_results['ui_components'].append({
                    'type': 'numeric_stats_card',
                    'title': f'Numeric Variable: {var_name}',
                    'statistics': {
                        'mean': round(stats.get('mean', 0), 3),
                        'median': round(stats.get('median', 0), 3),
                        'std': round(stats.get('std', 0), 3),
                        'min': round(stats.get('min', 0), 3),
                        'max': round(stats.get('max', 0), 3),
                        'count': stats.get('count', 0)
                    }
                })
        
        # Categorical statistics
        categorical_stats = basic_stats.get('categorical', {})
        if categorical_stats:
            for var_name, stats in categorical_stats.items():
                top_values = stats.get('top_values', {})
                formatted_results['ui_components'].append({
                    'type': 'categorical_stats_card',
                    'title': f'Categorical Variable: {var_name}',
                    'statistics': {
                        'total_responses': stats.get('total_responses', 0),
                        'unique_values': stats.get('unique_values', 0),
                        'top_categories': list(top_values.items())[:5] if top_values else []
                    }
                })
        
        return formatted_results

    def _format_inferential_results(self, results: Dict, formatted_results: Dict) -> Dict:
        """Format inferential analysis results for UI"""
        formatted_results['summary'] = {
            'analysis_type': results.get('analysis_type', 'inferential'),
            'tests_performed': len(results.get('tests_performed', [])),
            'sample_size': results.get('sample_size', 0)
        }
        
        # Tests performed
        tests = results.get('tests_performed', [])
        if tests:
            formatted_results['ui_components'].append({
                'type': 'info_card',
                'title': 'Statistical Tests Performed',
                'items': tests,
                'icon': 'calculator'
            })
        
        # Correlation analysis
        correlation_analysis = results.get('correlation_analysis', {})
        if correlation_analysis:
            formatted_results['ui_components'].append({
                'type': 'correlation_card',
                'title': 'Correlation Analysis',
                'data': correlation_analysis
            })
        
        # Group comparisons
        group_comparisons = results.get('group_comparisons', {})
        if group_comparisons:
            for group_var, comparison in group_comparisons.items():
                formatted_results['ui_components'].append({
                    'type': 'group_comparison_card',
                    'title': f'Group Analysis: {group_var}',
                    'groups': comparison.get('groups', {}),
                    'analysis': comparison.get('analysis', '')
                })
        
        return formatted_results

    def _format_qualitative_results(self, results: Dict, formatted_results: Dict) -> Dict:
        """Format qualitative analysis results for UI"""
        formatted_results['summary'] = {
            'analysis_type': results.get('analysis_type', 'qualitative'),
            'methods_applied': len(results.get('methods_applied', [])),
            'sample_size': results.get('sample_size', 0)
        }
        
        # Methods applied
        methods = results.get('methods_applied', [])
        if methods:
            formatted_results['ui_components'].append({
                'type': 'info_card',
                'title': 'Qualitative Methods Applied',
                'items': methods,
                'icon': 'text'
            })
        
        # Text analysis
        text_analysis = results.get('text_analysis', {})
        if text_analysis:
            for var_name, analysis in text_analysis.items():
                formatted_results['ui_components'].append({
                    'type': 'text_analysis_card',
                    'title': f'Text Analysis: {var_name}',
                    'statistics': {
                        'response_count': analysis.get('response_count', 0),
                        'average_length': round(analysis.get('average_length', 0), 1),
                        'unique_responses': analysis.get('unique_responses', 0)
                    },
                    'sample_responses': analysis.get('sample_responses', [])
                })
        
        # Categorical patterns
        categorical_patterns = results.get('categorical_patterns', {})
        if categorical_patterns:
            for var_name, pattern in categorical_patterns.items():
                formatted_results['ui_components'].append({
                    'type': 'pattern_card',
                    'title': f'Pattern Analysis: {var_name}',
                    'categories': pattern.get('categories', {}),
                    'diversity_index': pattern.get('diversity_index', 0),
                    'dominant_category': pattern.get('dominant_category', 'None')
                })
        
        return formatted_results

    def _format_recommendations_results(self, results: Dict, formatted_results: Dict) -> Dict:
        """Format recommendation results for UI"""
        if isinstance(results, list):
            recommendations = results
        else:
            recommendations = results.get('recommendations', [])
        
        formatted_results['summary'] = {
            'total_recommendations': len(recommendations),
            'analysis_type': 'recommendations'
        }
        
        for i, rec in enumerate(recommendations):
            priority = 'high' if i < 2 else 'medium' if i < 4 else 'low'
            formatted_results['ui_components'].append({
                'type': 'recommendation_card',
                'title': rec.get('method', 'Unknown Method'),
                'description': rec.get('rationale', 'No description available'),
                'priority': priority,
                'category': rec.get('category', 'general'),
                'action': rec.get('function_call', ''),
                'score': rec.get('score', 0)
            })
        
        return formatted_results

    def get_detailed_error_info(self, error_message: str, analysis_type: str = None) -> Dict:
        """Get detailed error information with troubleshooting steps"""
        error_info = {
            'error': error_message,
            'type': 'unknown',
            'severity': 'medium',
            'troubleshooting_steps': [],
            'quick_fixes': [],
            'need_help': False
        }
        
        # Categorize error types
        if 'no data' in error_message.lower() or 'no responses' in error_message.lower():
            error_info.update({
                'type': 'no_data',
                'severity': 'high',
                'troubleshooting_steps': [
                    "1. Verify you have collected responses for this project",
                    "2. Check Data Collection tab to start collecting responses",
                    "3. Ensure responses were saved successfully",
                    "4. Refresh the project data and try again"
                ],
                'quick_fixes': [
                    "Go to Data Collection tab",
                    "Select this project and collect responses",
                    "Return to Analytics when you have data"
                ]
            })
        elif 'backend' in error_message.lower() or 'network' in error_message.lower():
            error_info.update({
                'type': 'backend_error',
                'severity': 'medium',
                'troubleshooting_steps': [
                    "1. Check if analytics backend is running",
                    "2. Verify network connection",
                    "3. Try using local analysis instead",
                    "4. Contact administrator if problem persists"
                ],
                'quick_fixes': [
                    "Use local analysis capabilities",
                    "Check network connection",
                    "Try again in a few minutes"
                ]
            })
        elif 'insufficient' in error_message.lower() or 'sample size' in error_message.lower():
            error_info.update({
                'type': 'insufficient_data',
                'severity': 'medium',
                'troubleshooting_steps': [
                    "1. Collect more responses to increase sample size",
                    "2. Try descriptive analysis first",
                    "3. Consider different analysis methods",
                    "4. Review data quality requirements"
                ],
                'quick_fixes': [
                    "Try descriptive analysis instead",
                    "Collect more responses",
                    "Use auto-detection for recommendations"
                ]
            })
        else:
            error_info.update({
                'type': 'general_error',
                'severity': 'medium',
                'troubleshooting_steps': [
                    "1. Check your data quality and completeness",
                    "2. Try a different analysis type",
                    "3. Refresh and try again",
                    "4. Check the application logs for details"
                ],
                'quick_fixes': [
                    "Try auto-detection first",
                    "Check data quality",
                    "Refresh and retry"
                ],
                'need_help': True
            })
        
        return error_info

    def clear_cache(self):
        """Clear the analysis cache"""
        self.cache.clear()

    def get_cache_info(self) -> Dict:
        """Get information about cached analyses"""
        return {
            'cached_analyses': len(self.cache),
            'cache_keys': list(self.cache.keys())
        } 