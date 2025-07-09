"""
Shared utilities for analytics endpoints.
Consolidates common functions to reduce redundancy.
"""

import pandas as pd
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import sqlite3
from pathlib import Path


class AnalyticsUtils:
    """Shared utilities for analytics processing."""
    
    @staticmethod
    def get_django_db_connection():
        """Get connection to Django SQLite database."""
        # Path to Django database
        backend_dir = Path(__file__).parent.parent.parent.parent.parent  # Go up to backend/
        db_path = backend_dir / "db.sqlite3"
        
        if not db_path.exists():
            raise FileNotFoundError(f"Django database not found at {db_path}")
        
        return sqlite3.connect(str(db_path))
    
    @staticmethod
    def get_project_data(project_id: str) -> pd.DataFrame:
        """Get project data as DataFrame from Django database."""
        conn = AnalyticsUtils.get_django_db_connection()
        conn.row_factory = sqlite3.Row
        
        try:
            query = """
                SELECT 
                    r.id as response_id,
                    r.respondent_id,
                    r.response_value,
                    r.response_metadata,
                    r.collected_at,
                    q.question_text,
                    q.question_type,
                    q.options
                FROM responses_response r
                JOIN forms_question q ON r.question_id = q.id
                WHERE r.project_id = ?
                ORDER BY r.respondent_id, q.order_index
            """
            
            df = pd.read_sql_query(query, conn, params=[project_id])
            
            if df.empty:
                return pd.DataFrame()
            
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
            conn.close()
    
    @staticmethod
    def get_project_stats(project_id: str) -> Dict[str, Any]:
        """Get basic project statistics."""
        conn = AnalyticsUtils.get_django_db_connection()
        conn.row_factory = sqlite3.Row
        
        try:
            cursor = conn.cursor()
            
            # Get response count
            cursor.execute("""
                SELECT COUNT(*) as total_responses
                FROM responses_response 
                WHERE project_id = ?
            """, (project_id,))
            response_data = cursor.fetchone()
            
            # Get question count
            cursor.execute("""
                SELECT COUNT(*) as total_questions
                FROM forms_question 
                WHERE project_id = ? 
            """, (project_id,))
            question_data = cursor.fetchone()
            
            # Get unique respondents
            cursor.execute("""
                SELECT COUNT(DISTINCT respondent_id) as unique_respondents
                FROM responses_response 
                WHERE project_id = ?
            """, (project_id,))
            respondent_data = cursor.fetchone()
            
            total_responses = response_data['total_responses'] if response_data else 0
            total_questions = question_data['total_questions'] if question_data else 0
            unique_respondents = respondent_data['unique_respondents'] if respondent_data else 0
            
            # Calculate completion rate
            completion_rate = 0
            if total_questions > 0 and unique_respondents > 0:
                expected_total = total_questions * unique_respondents
                completion_rate = min(100, (total_responses / expected_total) * 100) if expected_total > 0 else 0
            
            return {
                'total_responses': total_responses,
                'total_questions': total_questions,
                'unique_respondents': unique_respondents,
                'completion_rate': round(completion_rate, 1),
                'sample_size': unique_respondents,
                'data_quality': 'good' if completion_rate > 80 else 'fair' if completion_rate > 50 else 'poor'
            }
            
        except Exception as e:
            print(f"Error getting project stats: {e}")
            return {}
        finally:
            conn.close()
    
    @staticmethod
    def analyze_data_characteristics(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze basic data characteristics."""
        if df.empty:
            return {'error': 'No data available'}
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        categorical_cols = []
        
        # Identify categorical columns (text with limited unique values)
        for col in text_cols:
            if df[col].nunique() <= 10:
                categorical_cols.append(col)
        
        return {
            'sample_size': len(df),
            'variable_count': len(df.columns),
            'numeric_variables': numeric_cols,
            'categorical_variables': categorical_cols,
            'text_variables': [col for col in text_cols if col not in categorical_cols],
            'missing_data_percentage': (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100,
            'completeness_score': (1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        }
    
    @staticmethod
    def run_descriptive_analysis(df: pd.DataFrame) -> Dict[str, Any]:
        """Run basic descriptive analysis."""
        if df.empty:
            return {'error': 'No data available'}
        
        results = {
            'basic_statistics': {},
            'summary': {
                'total_responses': len(df),
                'total_variables': len(df.columns),
                'analysis_timestamp': datetime.now().isoformat()
            }
        }
        
        # Numeric analysis
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            results['basic_statistics']['numeric'] = df[numeric_cols].describe().to_dict()
        
        # Categorical analysis
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            results['basic_statistics']['categorical'] = {}
            for col in categorical_cols:
                if df[col].nunique() <= 20:  # Only for reasonable number of categories
                    results['basic_statistics']['categorical'][col] = df[col].value_counts().head(10).to_dict()
        
        return results
    
    @staticmethod
    def run_correlation_analysis(df: pd.DataFrame) -> Dict[str, Any]:
        """Run correlation analysis on numeric variables."""
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) < 2:
            return {'error': 'Need at least 2 numeric variables for correlation analysis'}
        
        correlation_matrix = df[numeric_cols].corr()
        
        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'strong_correlations': AnalyticsUtils._find_strong_correlations(correlation_matrix),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def _find_strong_correlations(corr_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find strong correlations in correlation matrix."""
        strong_corr = []
        
        for i, var1 in enumerate(corr_matrix.columns):
            for j, var2 in enumerate(corr_matrix.columns):
                if i < j:  # Avoid duplicates and self-correlation
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) >= threshold:
                        strong_corr.append({
                            'variable_1': var1,
                            'variable_2': var2,
                            'correlation': round(corr_value, 3),
                            'strength': 'strong' if abs(corr_value) >= 0.8 else 'moderate'
                        })
        
        return strong_corr
    
    @staticmethod
    def generate_analysis_recommendations(characteristics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate smart analysis recommendations based on data characteristics."""
        recommendations = []
        
        if characteristics.get('sample_size', 0) == 0:
            return [{'method': 'no_data', 'message': 'No data available for analysis'}]
        
        # Always recommend basic statistics
        recommendations.append({
            'method': 'basic_statistics',
            'priority': 'high',
            'rationale': f"Basic statistics for {characteristics['sample_size']} responses",
            'estimated_time': '< 5 seconds'
        })
        
        # Correlation analysis if multiple numeric variables
        if len(characteristics.get('numeric_variables', [])) >= 2:
            recommendations.append({
                'method': 'correlation_analysis',
                'priority': 'high',
                'rationale': f"Correlation analysis for {len(characteristics['numeric_variables'])} numeric variables",
                'estimated_time': '< 10 seconds'
            })
        
        # Categorical analysis if categorical variables exist
        if len(characteristics.get('categorical_variables', [])) >= 1:
            recommendations.append({
                'method': 'categorical_analysis',
                'priority': 'medium',
                'rationale': f"Frequency analysis for {len(characteristics['categorical_variables'])} categorical variables",
                'estimated_time': '< 5 seconds'
            })
        
        # Text analysis if text variables exist
        if len(characteristics.get('text_variables', [])) >= 1:
            recommendations.append({
                'method': 'text_analysis',
                'priority': 'medium',
                'rationale': f"Basic text analysis for {len(characteristics['text_variables'])} text fields",
                'estimated_time': '< 15 seconds'
            })
        
        return recommendations
    
    @staticmethod
    def run_basic_text_analysis(df: pd.DataFrame, text_columns: List[str] = None) -> Dict[str, Any]:
        """Run basic text analysis."""
        if text_columns is None:
            text_columns = df.select_dtypes(include=['object']).columns.tolist()
        
        results = {
            'text_analysis': {},
            'summary': {
                'text_columns_analyzed': len(text_columns),
                'analysis_timestamp': datetime.now().isoformat()
            }
        }
        
        for col in text_columns:
            if col in df.columns:
                text_data = df[col].dropna().astype(str)
                if len(text_data) > 0:
                    results['text_analysis'][col] = {
                        'total_entries': len(text_data),
                        'average_length': text_data.str.len().mean(),
                        'total_words': text_data.str.split().str.len().sum(),
                        'unique_entries': text_data.nunique(),
                        'most_common': text_data.value_counts().head(5).to_dict()
                    }
        
        return results
    
    @staticmethod
    def format_api_response(status: str, data: Any, message: str = None) -> Dict[str, Any]:
        """Format standardized API response."""
        response = {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        if message:
            response['message'] = message
        
        return response
    
    @staticmethod
    def handle_analysis_error(error: Exception, context: str = "analysis") -> Dict[str, Any]:
        """Handle analysis errors consistently."""
        return AnalyticsUtils.format_api_response(
            status='error',
            data=None,
            message=f"Error in {context}: {str(error)}"
        ) 