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

logger = logging.getLogger(__name__)

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
    # Main analysis functions
    analyze_descriptive_data,
    quick_data_overview,
    auto_detect_analysis_needs,
    get_data_characteristics as get_descriptive_characteristics,
    generate_analysis_workflow,
    
    # Basic Statistics
    calculate_basic_stats,
    calculate_percentiles,
    calculate_grouped_stats,
    calculate_weighted_stats,
    calculate_correlation_matrix,
    calculate_covariance_matrix,
    
    # Distributions
    analyze_distribution,
    test_normality,
    calculate_skewness_kurtosis,
    fit_distribution,
    
    # Categorical Analysis
    analyze_categorical,
    calculate_chi_square,
    calculate_cramers_v,
    analyze_cross_tabulation,
    
    # Outlier Detection
    detect_outliers_iqr,
    detect_outliers_zscore,
    detect_outliers_isolation_forest,
    detect_outliers_mad,
    get_outlier_summary,
    
    # Missing Data
    analyze_missing_data,
    get_missing_patterns,
    calculate_missing_correlations,
    
    # Temporal Analysis
    analyze_temporal_patterns,
    calculate_time_series_stats,
    detect_seasonality,
    
    # Geospatial Analysis
    analyze_spatial_distribution,
    calculate_spatial_autocorrelation,
    create_location_clusters,
    
    # Summary Generation
    generate_full_report,
    generate_executive_summary,
    export_statistics
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
        """Generate smart analysis recommendations using auto-detection modules."""
        try:
            # Use the sophisticated auto-detection modules
            from app.analytics.descriptive.auto_detection import DescriptiveAutoDetector
            from app.analytics.qualitative.auto_detection import QualitativeAutoDetector
            
            # Create a simple DataFrame for the auto-detection modules
            import pandas as pd
            
            # Create a dummy DataFrame based on characteristics for auto-detection
            sample_size = characteristics.get('sample_size', 100)
            variable_count = characteristics.get('variable_count', 10)
            
            # Create synthetic data structure for auto-detection
            data_dict = {}
            
            # Add numeric variables
            numeric_vars = characteristics.get('numeric_variables', [])
            for var in numeric_vars[:5]:  # Limit to prevent too much processing
                data_dict[var] = [1.0] * min(sample_size, 100)
            
            # Add categorical variables  
            categorical_vars = characteristics.get('categorical_variables', [])
            for var in categorical_vars[:5]:
                data_dict[var] = ['category_1'] * min(sample_size, 100)
            
            # Add text variables
            text_vars = characteristics.get('text_variables', [])
            for var in text_vars[:3]:
                data_dict[var] = ['sample text response'] * min(sample_size, 100)
            
            # Ensure we have at least some data
            if not data_dict:
                data_dict = {'sample_var': [1] * min(sample_size, 100)}
            
            df = pd.DataFrame(data_dict)
            
            # Use descriptive auto-detector
            descriptive_detector = DescriptiveAutoDetector()
            descriptive_suggestions = descriptive_detector.suggest_analyses(df)
            
            # Use qualitative auto-detector for text data
            qualitative_suggestions = None
            if text_vars:
                qualitative_detector = QualitativeAutoDetector()
                sample_texts = ['sample survey response text'] * min(len(text_vars) * 10, 50)
                qualitative_suggestions = qualitative_detector.suggest_analyses(df, texts=sample_texts)
            
            # Combine suggestions
            recommendations = {
                'primary_recommendations': [],
                'secondary_recommendations': [],
                'data_quality_warnings': []
            }
            
            # Convert from standardized format to legacy format
            if descriptive_suggestions:
                for rec in descriptive_suggestions.primary_recommendations:
                    recommendations['primary_recommendations'].append({
                        'method': rec.method,
                        'score': rec.score,
                        'rationale': rec.rationale,
                        'function_call': rec.function_call or 'run_descriptive_analysis()',
                        'category': 'descriptive'
                    })
                
                for rec in descriptive_suggestions.secondary_recommendations:
                    recommendations['secondary_recommendations'].append({
                        'method': rec.method,
                        'score': rec.score,
                        'rationale': rec.rationale,
                        'function_call': rec.function_call or 'run_descriptive_analysis()',
                        'category': 'descriptive'
                    })
                
                recommendations['data_quality_warnings'].extend(descriptive_suggestions.data_quality_warnings)
            
            # Add qualitative recommendations
            if qualitative_suggestions:
                for rec in qualitative_suggestions.primary_recommendations:
                    recommendations['secondary_recommendations'].append({
                        'method': rec.method,
                        'score': rec.score,
                        'rationale': rec.rationale,
                        'function_call': rec.function_call or 'run_text_analysis()',
                        'category': 'qualitative'
                    })
            
            # Add data quality warnings based on characteristics
            completeness_score = characteristics.get('completeness_score', 100)
            if completeness_score < 80:
                recommendations['data_quality_warnings'].append(
                    f'Data completeness is {completeness_score:.1f}% - consider missing data analysis'
                )
            
            # If no sophisticated recommendations, fall back to basic ones
            if not recommendations['primary_recommendations']:
                sample_size = characteristics.get('sample_size', 0)
                numeric_vars = len(characteristics.get('numeric_variables', []))
                categorical_vars = len(characteristics.get('categorical_variables', []))
                text_vars = len(characteristics.get('text_variables', []))
                
                recommendations['primary_recommendations'].append({
                    'method': 'basic_statistics',
                    'score': 0.9,
                    'rationale': f'Basic statistics suitable for {sample_size} responses',
                    'function_call': 'run_descriptive_analysis()',
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
            
            # Apply numpy type conversion to ensure serialization
            return AnalyticsUtils.convert_numpy_types(recommendations)
            
        except Exception as e:
            logger.error(f"Error generating sophisticated recommendations: {e}")
            # Fallback to basic recommendations
            return AnalyticsUtils._generate_basic_recommendations(characteristics)
    
    @staticmethod
    def _generate_basic_recommendations(characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic fallback recommendations when sophisticated auto-detection fails."""
        recommendations = {
            'primary_recommendations': [],
            'secondary_recommendations': [],
            'data_quality_warnings': []
        }
        
        try:
            sample_size = characteristics.get('sample_size', 0)
            numeric_vars = len(characteristics.get('numeric_variables', []))
            categorical_vars = len(characteristics.get('categorical_variables', []))
            text_vars = len(characteristics.get('text_variables', []))
            
            if sample_size > 0:
                # Basic statistics always recommended
                recommendations['primary_recommendations'].append({
                    'method': 'basic_statistics',
                    'score': 0.9,
                    'rationale': f'Basic statistics suitable for {sample_size} responses',
                    'function_call': 'run_descriptive_analysis()',
                    'category': 'descriptive'
                })
                
                if numeric_vars >= 2:
                    recommendations['secondary_recommendations'].append({
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
            
            return AnalyticsUtils.convert_numpy_types(recommendations)
            
        except Exception as e:
            logger.error(f"Error generating basic recommendations: {e}")
            return AnalyticsUtils.convert_numpy_types(recommendations)
    
    @staticmethod
    def run_descriptive_analysis(df: pd.DataFrame, analysis_type: str = "comprehensive", 
                                target_variables: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run comprehensive descriptive statistical analysis."""
        if df.empty:
            return {'error': 'No data available for analysis'}
        
        try:
            # Use the comprehensive descriptive analytics functions
            results = analyze_descriptive_data(
                df, 
                analysis_type=analysis_type,
                target_variables=target_variables
            )
            
            # Add summary information
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            
            results['summary'] = {
                'analysis_type': analysis_type,
                'variables_analyzed': len(df.columns),
                'observations': len(df),
                'numeric_variables': len(numeric_cols),
                'categorical_variables': len(categorical_cols),
                'datetime_variables': len(datetime_cols),
                'data_shape': df.shape,
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
            }
            
            # Apply numpy type conversion
            return AnalyticsUtils.convert_numpy_types(results)
            
        except Exception as e:
            logger.error(f"Error in descriptive analysis: {e}")
            return {'error': f'Descriptive analysis failed: {str(e)}'}
    
    @staticmethod
    def run_basic_statistics(df: pd.DataFrame, variables: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run basic statistical analysis only."""
        if df.empty:
            return {'error': 'No data available for analysis'}
        
        try:
            # Select variables or use all numeric ones
            if variables:
                numeric_cols = [col for col in variables if col in df.columns and 
                               pd.api.types.is_numeric_dtype(df[col])]
            else:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_cols:
                return {'error': 'No numeric variables found for basic statistics'}
            
            basic_stats = calculate_basic_stats(df, numeric_cols)
            percentiles = calculate_percentiles(df, numeric_cols)
            
            result = {
                'basic_statistics': basic_stats,
                'percentiles': percentiles,
                'summary': {
                    'variables_analyzed': len(numeric_cols),
                    'variable_names': numeric_cols,
                    'observations': len(df)
                }
            }
            
            return AnalyticsUtils.convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"Error in basic statistics: {e}")
            return {'error': f'Basic statistics failed: {str(e)}'}
    
    @staticmethod
    def run_distribution_analysis(df: pd.DataFrame, variables: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run distribution analysis for numeric variables."""
        if df.empty:
            return {'error': 'No data available for analysis'}
        
        try:
            # Select variables or use all numeric ones
            if variables:
                numeric_cols = [col for col in variables if col in df.columns and 
                               pd.api.types.is_numeric_dtype(df[col])]
            else:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_cols:
                return {'error': 'No numeric variables found for distribution analysis'}
            
            results = {}
            for col in numeric_cols:
                try:
                    series = df[col].dropna()
                    if len(series) > 0:
                        results[col] = {
                            'distribution_analysis': analyze_distribution(series),
                            'normality_test': test_normality(series),
                            'skewness_kurtosis': calculate_skewness_kurtosis(series),
                            'outliers': detect_outliers_iqr(series)
                        }
                except Exception as e:
                    results[col] = {'error': f'Analysis failed: {str(e)}'}
            
            result = {
                'distribution_analysis': results,
                'summary': {
                    'variables_analyzed': len(results),
                    'variable_names': list(results.keys()),
                    'observations': len(df)
                }
            }
            
            return AnalyticsUtils.convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"Error in distribution analysis: {e}")
            return {'error': f'Distribution analysis failed: {str(e)}'}
    
    @staticmethod
    def run_categorical_analysis(df: pd.DataFrame, variables: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run categorical analysis for categorical variables."""
        if df.empty:
            return {'error': 'No data available for analysis'}
        
        try:
            # Select variables or use all categorical ones
            if variables:
                categorical_cols = [col for col in variables if col in df.columns and 
                                  df[col].dtype in ['object', 'category']]
            else:
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if not categorical_cols:
                return {'error': 'No categorical variables found for analysis'}
            
            results = {}
            for col in categorical_cols:
                try:
                    series = df[col].dropna()
                    if len(series) > 0:
                        results[col] = analyze_categorical(series)
                except Exception as e:
                    results[col] = {'error': f'Analysis failed: {str(e)}'}
            
            # Cross-tabulation analysis for pairs of categorical variables
            cross_tabs = {}
            if len(categorical_cols) >= 2:
                for i, col1 in enumerate(categorical_cols):
                    for col2 in categorical_cols[i+1:]:
                        try:
                            cross_tab_key = f"{col1}_vs_{col2}"
                            cross_tabs[cross_tab_key] = analyze_cross_tabulation(df, col1, col2)
                        except Exception as e:
                            cross_tabs[cross_tab_key] = {'error': f'Cross-tabulation failed: {str(e)}'}
            
            result = {
                'categorical_analysis': results,
                'cross_tabulations': cross_tabs,
                'summary': {
                    'variables_analyzed': len(results),
                    'variable_names': list(results.keys()),
                    'cross_tabs_computed': len(cross_tabs),
                    'observations': len(df)
                }
            }
            
            return AnalyticsUtils.convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"Error in categorical analysis: {e}")
            return {'error': f'Categorical analysis failed: {str(e)}'}
    
    @staticmethod
    def run_outlier_analysis(df: pd.DataFrame, variables: Optional[List[str]] = None, 
                           methods: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run comprehensive outlier detection analysis."""
        if df.empty:
            return {'error': 'No data available for analysis'}
        
        try:
            # Select variables or use all numeric ones
            if variables:
                numeric_cols = [col for col in variables if col in df.columns and 
                               pd.api.types.is_numeric_dtype(df[col])]
            else:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_cols:
                return {'error': 'No numeric variables found for outlier analysis'}
            
            # Default methods if not specified
            if not methods:
                methods = ['iqr', 'zscore', 'isolation_forest'] if len(df) > 100 else ['iqr', 'zscore']
            
            results = {}
            for col in numeric_cols:
                try:
                    series = df[col].dropna()
                    if len(series) > 0:
                        col_results = {}
                        
                        if 'iqr' in methods:
                            col_results['iqr_outliers'] = detect_outliers_iqr(series)
                        if 'zscore' in methods:
                            col_results['zscore_outliers'] = detect_outliers_zscore(series)
                        if 'isolation_forest' in methods and len(series) > 50:
                            col_results['isolation_forest_outliers'] = detect_outliers_isolation_forest(series)
                        if 'mad' in methods:
                            col_results['mad_outliers'] = detect_outliers_mad(series)
                        
                        results[col] = col_results
                except Exception as e:
                    results[col] = {'error': f'Outlier detection failed: {str(e)}'}
            
            # Overall summary
            outlier_summary = get_outlier_summary(df, numeric_cols)
            
            result = {
                'outlier_analysis': results,
                'outlier_summary': outlier_summary,
                'methods_used': methods,
                'summary': {
                    'variables_analyzed': len(results),
                    'variable_names': list(results.keys()),
                    'observations': len(df)
                }
            }
            
            return AnalyticsUtils.convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"Error in outlier analysis: {e}")
            return {'error': f'Outlier analysis failed: {str(e)}'}
    
    @staticmethod
    def run_missing_data_analysis(df: pd.DataFrame) -> Dict[str, Any]:
        """Run comprehensive missing data analysis."""
        if df.empty:
            return {'error': 'No data available for analysis'}
        
        try:
            missing_analysis = analyze_missing_data(df)
            missing_patterns = get_missing_patterns(df)
            missing_correlations = calculate_missing_correlations(df)
            
            result = {
                'missing_data_analysis': missing_analysis,
                'missing_patterns': missing_patterns,
                'missing_correlations': missing_correlations,
                'summary': {
                    'total_missing_values': df.isnull().sum().sum(),
                    'missing_percentage': (df.isnull().sum().sum() / df.size) * 100,
                    'columns_with_missing': df.isnull().sum()[df.isnull().sum() > 0].to_dict(),
                    'complete_cases': len(df.dropna()),
                    'observations': len(df)
                }
            }
            
            return AnalyticsUtils.convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"Error in missing data analysis: {e}")
            return {'error': f'Missing data analysis failed: {str(e)}'}
    
    @staticmethod
    def run_temporal_analysis(df: pd.DataFrame, date_column: str, 
                            value_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run temporal pattern analysis."""
        if df.empty:
            return {'error': 'No data available for analysis'}
        
        if date_column not in df.columns:
            return {'error': f'Date column "{date_column}" not found in data'}
        
        try:
            # Convert date column if needed
            if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
                df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            
            # Select value columns or use all numeric ones
            if value_columns:
                numeric_cols = [col for col in value_columns if col in df.columns and 
                               pd.api.types.is_numeric_dtype(df[col])]
            else:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_cols:
                return {'error': 'No numeric variables found for temporal analysis'}
            
            temporal_patterns = analyze_temporal_patterns(df, date_column, numeric_cols)
            time_series_stats = calculate_time_series_stats(df, date_column, numeric_cols)
            
            # Seasonality detection for each numeric column
            seasonality_results = {}
            for col in numeric_cols:
                try:
                    seasonality_results[col] = detect_seasonality(df, date_column, col)
                except Exception as e:
                    seasonality_results[col] = {'error': f'Seasonality detection failed: {str(e)}'}
            
            result = {
                'temporal_patterns': temporal_patterns,
                'time_series_statistics': time_series_stats,
                'seasonality_analysis': seasonality_results,
                'summary': {
                    'date_column': date_column,
                    'value_columns': numeric_cols,
                    'date_range': {
                        'start': df[date_column].min().isoformat() if pd.notnull(df[date_column].min()) else None,
                        'end': df[date_column].max().isoformat() if pd.notnull(df[date_column].max()) else None
                    },
                    'observations': len(df)
                }
            }
            
            return AnalyticsUtils.convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"Error in temporal analysis: {e}")
            return {'error': f'Temporal analysis failed: {str(e)}'}
    
    @staticmethod
    def run_geospatial_analysis(df: pd.DataFrame, lat_column: str, lon_column: str) -> Dict[str, Any]:
        """Run geospatial analysis."""
        if df.empty:
            return {'error': 'No data available for analysis'}
        
        if lat_column not in df.columns or lon_column not in df.columns:
            return {'error': f'Location columns "{lat_column}" or "{lon_column}" not found in data'}
        
        try:
            spatial_distribution = analyze_spatial_distribution(df, lat_column, lon_column)
            spatial_autocorr = calculate_spatial_autocorrelation(df, lat_column, lon_column)
            location_clusters = create_location_clusters(df, lat_column, lon_column)
            
            result = {
                'spatial_distribution': spatial_distribution,
                'spatial_autocorrelation': spatial_autocorr,
                'location_clusters': location_clusters,
                'summary': {
                    'latitude_column': lat_column,
                    'longitude_column': lon_column,
                    'valid_coordinates': len(df.dropna(subset=[lat_column, lon_column])),
                    'observations': len(df)
                }
            }
            
            return AnalyticsUtils.convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"Error in geospatial analysis: {e}")
            return {'error': f'Geospatial analysis failed: {str(e)}'}
    
    @staticmethod
    def run_data_quality_analysis(df: pd.DataFrame) -> Dict[str, Any]:
        """Run comprehensive data quality analysis."""
        if df.empty:
            return {'error': 'No data available for analysis'}
        
        try:
            # Use the data quality analysis type
            results = analyze_descriptive_data(df, analysis_type="quality")
            
            # Add additional quality metrics
            quality_metrics = {
                'completeness': {
                    'overall_completeness': (1 - df.isnull().sum().sum() / df.size) * 100,
                    'column_completeness': ((1 - df.isnull().sum() / len(df)) * 100).to_dict()
                },
                'consistency': {
                    'duplicate_rows': df.duplicated().sum(),
                    'duplicate_percentage': (df.duplicated().sum() / len(df)) * 100
                },
                'validity': {
                    'data_types': df.dtypes.astype(str).to_dict(),
                    'unique_values_per_column': df.nunique().to_dict()
                }
            }
            
            results['quality_metrics'] = quality_metrics
            results['summary'] = {
                'analysis_type': 'data_quality',
                'overall_quality_score': min(100, max(0, 100 - (df.isnull().sum().sum() / df.size) * 100 - 
                                           (df.duplicated().sum() / len(df)) * 10)),
                'observations': len(df),
                'variables': len(df.columns)
            }
            
            return AnalyticsUtils.convert_numpy_types(results)
            
        except Exception as e:
            logger.error(f"Error in data quality analysis: {e}")
            return {'error': f'Data quality analysis failed: {str(e)}'}
    
    @staticmethod
    def generate_comprehensive_report(df: pd.DataFrame, include_plots: bool = False) -> Dict[str, Any]:
        """Generate a comprehensive descriptive statistics report."""
        if df.empty:
            return {'error': 'No data available for analysis'}
        
        try:
            # Generate comprehensive analysis
            comprehensive_results = analyze_descriptive_data(df, analysis_type="comprehensive")
            
            # Generate executive summary
            executive_summary = generate_executive_summary(df)
            
            # Generate full report
            full_report = generate_full_report(df)
            
            # Generate analysis workflow recommendations
            workflow = generate_analysis_workflow(df)
            
            result = {
                'comprehensive_analysis': comprehensive_results,
                'executive_summary': executive_summary,
                'full_report': full_report,
                'recommended_workflow': workflow,
                'report_metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'data_shape': df.shape,
                    'include_plots': include_plots,
                    'report_type': 'comprehensive_descriptive'
                }
            }
            
            return AnalyticsUtils.convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return {'error': f'Report generation failed: {str(e)}'}
    
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