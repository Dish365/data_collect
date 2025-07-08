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
        """Get project data as pandas DataFrame for analysis"""
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

    def get_data_characteristics(self, project_id: str) -> Dict:
        """Get data characteristics for a project using streamlined API"""
        try:
            # Try backend API first
            result = self._make_analytics_request(f'project/{project_id}/data-characteristics')
            
            if 'error' not in result:
                return result.get('characteristics', result)
                
            # Fallback to local analysis
            df = self.get_project_data(project_id)
            
            if df.empty:
                return {'error': 'No data available'}
                
            characteristics = {
                'sample_size': len(df),
                'variable_count': len(df.columns),
                'completeness_score': (1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100,
                'numeric_variables': [],
                'categorical_variables': [],
                'text_variables': [],
                'data_quality': {
                    'missing_data_percentage': (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100,
                    'duplicate_responses': df.duplicated().sum(),
                    'outliers_detected': 0  # Simplified for now
                }
            }
            
            # Analyze variable types
            for col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    characteristics['numeric_variables'].append(col)
                elif len(df[col].unique()) < 10:  # Simplified categorical detection
                    characteristics['categorical_variables'].append(col)
                else:
                    characteristics['text_variables'].append(col)
                    
            return characteristics
            
        except Exception as e:
            return {'error': f'Error analyzing data characteristics: {str(e)}'}

    def get_analysis_recommendations(self, project_id: str) -> Dict:
        """Get smart analysis recommendations from streamlined API"""
        cache_key = f"recommendations_{project_id}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_time = self.cache[cache_key].get('timestamp', 0)
            if datetime.now().timestamp() - cached_time < 300:  # 5 minutes cache
                return self.cache[cache_key]['data']
        
        try:
            # Call streamlined recommendations API
            result = self._make_analytics_request(f'project/{project_id}/recommendations')
            
            if 'error' in result:
                # Fallback to local recommendations if backend fails
                characteristics = self.get_data_characteristics(project_id)
                return self._generate_local_recommendations(characteristics)
            
            # Cache the results
            self.cache[cache_key] = {
                'data': result,
                'timestamp': datetime.now().timestamp()
            }
            
            return result
            
        except Exception as e:
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
            # Try backend API first
            result = self._make_analytics_request(f'project/{project_id}/analyze', method='POST', data={'analysis_type': 'descriptive'})
            
            if 'error' not in result:
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
            results = {
                'basic_statistics': {},
                'summary': {
                    'total_responses': len(df),
                    'total_variables': len(df.columns),
                    'completeness': (1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
                }
            }
            
            # Basic statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                results['basic_statistics']['numeric'] = df[numeric_cols].describe().to_dict()
                
            # Frequency analysis for categorical columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                results['basic_statistics']['categorical'] = {}
                for col in categorical_cols:
                    value_counts = df[col].value_counts().head(10).to_dict()
                    results['basic_statistics']['categorical'][col] = value_counts
                    
            return results
            
        except Exception as e:
            return {'error': f'Local descriptive analysis failed: {str(e)}'}

    def run_inferential_analysis(self, project_id: str, analysis_config: Dict) -> Dict:
        """Run inferential statistical analysis"""
        try:
            payload = {
                'project_id': project_id,
                'analysis_config': analysis_config
            }
            
            result = self._make_analytics_request('inferential/', method='POST', data=payload)
            
            if 'error' in result:
                return {'error': 'Inferential analysis not available offline'}
                
            return result
            
        except Exception as e:
            return {'error': f'Inferential analysis failed: {str(e)}'}

    def run_qualitative_analysis(self, project_id: str, analysis_config: Dict) -> Dict:
        """Run qualitative text analysis"""
        try:
            payload = {
                'project_id': project_id,
                'analysis_config': analysis_config
            }
            
            result = self._make_analytics_request('qualitative/', method='POST', data=payload)
            
            if 'error' in result:
                return self._run_local_qualitative_analysis(project_id, analysis_config)
                
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