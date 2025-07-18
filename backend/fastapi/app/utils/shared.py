"""
Shared utilities for analytics operations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import logging
from core.database import get_project_data, get_project_stats

# Import analytics modules
from app.analytics.auto_detect.survey_detector import SurveyDetector
from app.analytics.auto_detect.base_detector import StandardizedDataProfiler, DataCharacteristics

# Try to import the unified auto-detector
try:
    from app.analytics.auto_detect import UnifiedAutoDetector, create_auto_detector
    UNIFIED_AUTO_DETECTOR_AVAILABLE = True
except ImportError:
    UNIFIED_AUTO_DETECTOR_AVAILABLE = False
    logger.warning("UnifiedAutoDetector not available, using basic auto-detection")
from app.analytics.descriptive import (
    calculate_basic_stats,
    analyze_distribution,
    analyze_categorical,
    generate_full_report
)
from app.analytics.qualitative import (
    analyze_sentiment,
    analyze_sentiment_batch
)

# Import text analysis functions
try:
    from app.analytics.qualitative.text_analysis import analyze_text_frequency, preprocess_text
except ImportError:
    # Fallback implementations
    def analyze_text_frequency(text: str):
        """Fallback text frequency analysis"""
        words = text.lower().split()
        from collections import Counter
        return dict(Counter(words))
    
    def preprocess_text(text: str):
        """Fallback text preprocessing"""
        return text.lower().split()

logger = logging.getLogger(__name__)

class AnalyticsUtils:
    """Comprehensive analytics utilities for the FastAPI endpoints."""
    
    @staticmethod
    async def get_project_data(project_id: str) -> pd.DataFrame:
        """Get project data as pandas DataFrame."""
        try:
            data = await get_project_data(project_id)
            if not data:
                return pd.DataFrame()
            
            df = pd.DataFrame(data)
            return AnalyticsUtils._prepare_dataframe(df)
        except Exception as e:
            logger.error(f"Error getting project data: {e}")
            return pd.DataFrame()
    
    @staticmethod
    async def get_project_stats(project_id: str) -> Dict[str, Any]:
        """Get basic project statistics."""
        try:
            return await get_project_stats(project_id)
        except Exception as e:
            logger.error(f"Error getting project stats: {e}")
            return {}
    
    @staticmethod
    def _prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Prepare DataFrame for analysis."""
        if df.empty:
            return df
        
        # Handle complex data types that cause issues with analytics
        for col in df.columns:
            if col in ['choice_selections', 'location_data', 'device_info', 'response_metadata']:
                # Convert complex data to strings for analysis
                df[col] = df[col].astype(str)
        
        # Convert datetime columns
        if 'collected_at' in df.columns:
            df['collected_at'] = pd.to_datetime(df['collected_at'], errors='coerce')
        if 'datetime_value' in df.columns:
            df['datetime_value'] = pd.to_datetime(df['datetime_value'], errors='coerce')
        
        # Convert numeric columns
        if 'numeric_value' in df.columns:
            df['numeric_value'] = pd.to_numeric(df['numeric_value'], errors='coerce')
        
        # Convert data quality score
        if 'data_quality_score' in df.columns:
            df['data_quality_score'] = pd.to_numeric(df['data_quality_score'], errors='coerce')
        
        # Drop columns that are not useful for analysis
        columns_to_drop = ['response_id', 'device_info', 'location_data']
        df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
        
        return df
    
    @staticmethod
    def convert_numpy_types(obj):
        """Convert numpy types to native Python types for JSON serialization"""
        if isinstance(obj, dict):
            return {key: AnalyticsUtils.convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [AnalyticsUtils.convert_numpy_types(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif pd.isna(obj):
            return None
        else:
            return obj
    
    @staticmethod
    def analyze_data_characteristics(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data characteristics for recommendations."""
        if df.empty:
            return {
                'sample_size': 0,
                'variable_count': 0,
                'numeric_variables': [],
                'categorical_variables': [],
                'text_variables': [],
                'datetime_variables': [],
                'completeness_score': 0
            }
        
        try:
            # Use the standardized data profiler
            profiler = StandardizedDataProfiler()
            characteristics = profiler.profile_data(df)
            
            # Convert to the expected format and ensure all numpy types are converted
            result = {
                'sample_size': int(characteristics.n_observations),
                'variable_count': int(characteristics.n_variables),
                'numeric_variables': [col for col, dtype in characteristics.variable_types.items() 
                                    if dtype.value in ['numeric_continuous', 'numeric_discrete']],
                'categorical_variables': [col for col, dtype in characteristics.variable_types.items() 
                                        if dtype.value in ['categorical', 'ordinal', 'binary']],
                'text_variables': [col for col, dtype in characteristics.variable_types.items() 
                                 if dtype.value == 'text'],
                'datetime_variables': [col for col, dtype in characteristics.variable_types.items() 
                                     if dtype.value == 'datetime'],
                'completeness_score': float(characteristics.completeness_score),
                'missing_data_summary': characteristics.missing_patterns.get('variables_with_missing', {}),
                'data_quality': {
                    'duplicate_rows': int(characteristics.duplicate_rows),
                    'constant_columns': characteristics.constant_columns,
                    'missing_percentage': float(characteristics.missing_percentage)
                }
            }
            
            # Apply numpy type conversion to the entire result
            return AnalyticsUtils.convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"Error in analyze_data_characteristics: {e}")
            # Fallback to simple analysis
            result = {
                'sample_size': len(df),
                'variable_count': len(df.columns),
                'numeric_variables': list(df.select_dtypes(include=[np.number]).columns),
                'categorical_variables': list(df.select_dtypes(include=['object', 'category']).columns),
                'text_variables': [],
                'datetime_variables': list(df.select_dtypes(include=['datetime64']).columns),
                'completeness_score': 100 - (df.isna().sum().sum() / df.size * 100),
                'missing_data_summary': {},
                'data_quality': {
                    'duplicate_rows': df.duplicated().sum(),
                    'constant_columns': [],
                    'missing_percentage': df.isna().sum().sum() / df.size * 100
                }
            }
            
            # Apply numpy type conversion to the fallback result
            return AnalyticsUtils.convert_numpy_types(result)
    
    @staticmethod
    def generate_analysis_recommendations(characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate smart analysis recommendations."""
        recommendations = {
            'primary_recommendations': [],
            'secondary_recommendations': [],
            'data_quality_warnings': []
        }
        
        try:
            sample_size = characteristics.get('sample_size', 0)
            
            if sample_size > 0:
                # Basic statistics always recommended
                recommendations['primary_recommendations'].append({
                    'method': 'basic_statistics',
                    'score': 0.9,
                    'rationale': f'Basic statistics suitable for {sample_size} responses',
                    'function_call': 'run_descriptive_analysis()',
                    'category': 'descriptive'
                })
                
                # Conditional recommendations based on data characteristics
                numeric_vars = len(characteristics.get('numeric_variables', []))
                categorical_vars = len(characteristics.get('categorical_variables', []))
                text_vars = len(characteristics.get('text_variables', []))
                
                if numeric_vars >= 2:
                    recommendations['primary_recommendations'].append({
                        'method': 'correlation_analysis',
                        'score': 0.85,
                        'rationale': f'Correlation analysis for {numeric_vars} numeric variables',
                        'function_call': 'run_correlation_analysis()',
                        'category': 'descriptive'
                    })
                    
                if categorical_vars >= 1:
                    recommendations['secondary_recommendations'].append({
                        'method': 'categorical_analysis',
                        'score': 0.75,
                        'rationale': f'Categorical analysis for {categorical_vars} categorical variables',
                        'function_call': 'run_categorical_analysis()',
                        'category': 'descriptive'
                    })
                    
                if text_vars >= 1:
                    recommendations['secondary_recommendations'].append({
                        'method': 'text_analysis',
                        'score': 0.8,
                        'rationale': f'Text analysis for {text_vars} text fields',
                        'function_call': 'run_text_analysis()',
                        'category': 'qualitative'
                    })
            
            # Data quality warnings
            completeness_score = characteristics.get('completeness_score', 100)
            if completeness_score < 80:
                recommendations['data_quality_warnings'].append(
                    f'Data completeness is {completeness_score:.1f}% - consider missing data analysis'
                )
            
            # Apply numpy type conversion to ensure serialization
            return AnalyticsUtils.convert_numpy_types(recommendations)
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return AnalyticsUtils.convert_numpy_types(recommendations)
    
    @staticmethod
    def run_descriptive_analysis(df: pd.DataFrame) -> Dict[str, Any]:
        """Run descriptive statistical analysis."""
        if df.empty:
            return {'error': 'No data available for analysis'}
        
        try:
            # Use the existing descriptive analytics functions
            basic_stats = calculate_basic_stats(df)
            
            # Convert to expected format
            result = {
                'basic_statistics': basic_stats,
                'summary': {
                    'variables_analyzed': len(df.columns),
                    'observations': len(df),
                    'numeric_variables': len(df.select_dtypes(include=[np.number]).columns),
                    'categorical_variables': len(df.select_dtypes(include=['object', 'category']).columns)
                }
            }
            
            # Apply numpy type conversion
            return AnalyticsUtils.convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"Error in descriptive analysis: {e}")
            return {'error': f'Descriptive analysis failed: {str(e)}'}
    
    @staticmethod
    def run_correlation_analysis(df: pd.DataFrame) -> Dict[str, Any]:
        """Run correlation analysis."""
        if df.empty:
            return {'error': 'No data available for correlation analysis'}
        
        try:
            # Get numeric columns for correlation
            numeric_df = df.select_dtypes(include=[np.number])
            
            if len(numeric_df.columns) < 2:
                return {'error': 'Need at least 2 numeric variables for correlation analysis'}
            
            # Calculate correlation matrix
            correlation_matrix = numeric_df.corr()
            
            result = {
                'correlation_matrix': correlation_matrix.to_dict(),
                'variables_included': list(numeric_df.columns),
                'summary': {
                    'variables_analyzed': len(numeric_df.columns),
                    'strongest_correlation': float(correlation_matrix.abs().unstack().sort_values(ascending=False).iloc[1])
                }
            }
            
            # Apply numpy type conversion
            return AnalyticsUtils.convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"Error in correlation analysis: {e}")
            return {'error': f'Correlation analysis failed: {str(e)}'}
    
    @staticmethod
    def run_basic_text_analysis(df: pd.DataFrame, text_columns: List[str]) -> Dict[str, Any]:
        """Run basic text analysis."""
        if df.empty or not text_columns:
            return {'error': 'No text data available for analysis'}
        
        try:
            results = {}
            
            for col in text_columns:
                if col in df.columns:
                    text_data = df[col].dropna()
                    if len(text_data) > 0:
                        # Basic text statistics
                        results[col] = {
                            'total_entries': len(text_data),
                            'average_length': float(text_data.str.len().mean()),
                            'max_length': int(text_data.str.len().max()),
                            'min_length': int(text_data.str.len().min()),
                            'word_count': int(text_data.str.split().str.len().sum()),
                            'unique_entries': int(text_data.nunique())
                        }
            
            result = {
                'text_analysis': results,
                'summary': {
                    'columns_analyzed': len(results),
                    'total_text_entries': sum(r['total_entries'] for r in results.values())
                }
            }
            
            # Apply numpy type conversion
            return AnalyticsUtils.convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"Error in text analysis: {e}")
            return {'error': f'Text analysis failed: {str(e)}'}
    
    @staticmethod
    def format_api_response(status: str, data: Any, message: str = None) -> Dict[str, Any]:
        """Format API response with proper serialization."""
        response = {
            'status': status,
            'data': AnalyticsUtils.convert_numpy_types(data) if data is not None else None,
            'timestamp': datetime.now().isoformat()
        }
        
        if message:
            response['message'] = message
            
        return response
    
    @staticmethod
    def handle_analysis_error(error: Exception, context: str) -> Dict[str, Any]:
        """Handle analysis errors with proper formatting."""
        error_message = f"{context} failed: {str(error)}"
        logger.error(error_message)
        
        return AnalyticsUtils.format_api_response('error', None, error_message)
    
    @staticmethod
    def get_django_db_connection():
        """Get Django database connection."""
        from core.database import get_django_db_connection
        return get_django_db_connection() 