"""
Streamlined analytics endpoints - consolidates all analytics functionality.
This replaces the complex auto_detect, descriptive, inferential, and qualitative endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import pandas as pd

from core.database import get_db
from app.utils.shared import AnalyticsUtils

router = APIRouter()

@router.get("/project/{project_id}/stats")
async def get_project_stats(
    project_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get basic project statistics.
    
    Args:
        project_id: Project identifier
        db: Database session
        
    Returns:
        Project statistics
    """
    try:
        stats = await AnalyticsUtils.get_project_stats(project_id)
        return AnalyticsUtils.format_api_response('success', stats)
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "project stats")

@router.get("/project/{project_id}/data-characteristics")
async def get_data_characteristics(
    project_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get data characteristics for a project.
    
    Args:
        project_id: Project identifier
        db: Database session
        
    Returns:
        Data characteristics and analysis recommendations
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', 
                None, 
                'No data available for this project'
            )
        
        characteristics = AnalyticsUtils.analyze_data_characteristics(df)
        recommendations = AnalyticsUtils.generate_analysis_recommendations(characteristics)
        
        return AnalyticsUtils.format_api_response('success', {
            'characteristics': characteristics,
            'recommendations': recommendations
        })
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "data characteristics")

@router.post("/project/{project_id}/analyze")
async def analyze_project_data(
    project_id: str,
    analysis_type: str = "auto",
    target_variables: Optional[List[str]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run comprehensive analysis on project data.
    
    Args:
        project_id: Project identifier
        analysis_type: Type of analysis (auto, descriptive, basic, comprehensive, 
                      distribution, categorical, outlier, missing, temporal, geospatial, quality)
        target_variables: Optional list of specific variables to analyze
        db: Database session
        
    Returns:
        Analysis results
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', 
                None, 
                'No data available for analysis'
            )
        
        # Get data characteristics first
        characteristics = AnalyticsUtils.analyze_data_characteristics(df)
        
        results = {
            'project_id': project_id,
            'analysis_type': analysis_type,
            'data_characteristics': characteristics,
            'analyses': {}
        }
        
        if analysis_type == "auto":
            # Run all applicable analyses based on data characteristics
            results['analyses']['descriptive'] = AnalyticsUtils.run_descriptive_analysis(
                df, "comprehensive", target_variables
            )
            
            if len(characteristics.get('numeric_variables', [])) >= 2:
                results['analyses']['correlation'] = AnalyticsUtils.run_correlation_analysis(df)
            
            if len(characteristics.get('text_variables', [])) >= 1:
                results['analyses']['text'] = AnalyticsUtils.run_basic_text_analysis(
                    df, characteristics['text_variables']
                )
            
            # Add missing data analysis if there's missing data
            if characteristics.get('missing_percentage', 0) > 0:
                results['analyses']['missing_data'] = AnalyticsUtils.run_missing_data_analysis(df)
        
        elif analysis_type == "descriptive":
            results['analyses']['descriptive'] = AnalyticsUtils.run_descriptive_analysis(
                df, "comprehensive", target_variables
            )
        
        elif analysis_type == "basic":
            results['analyses']['basic_statistics'] = AnalyticsUtils.run_basic_statistics(
                df, target_variables
            )
        
        elif analysis_type == "comprehensive":
            results['analyses'] = {
                'comprehensive_report': AnalyticsUtils.generate_comprehensive_report(df),
                'descriptive': AnalyticsUtils.run_descriptive_analysis(df, "comprehensive"),
                'data_quality': AnalyticsUtils.run_data_quality_analysis(df)
            }
        
        elif analysis_type == "distribution":
            results['analyses']['distribution'] = AnalyticsUtils.run_distribution_analysis(
                df, target_variables
            )
        
        elif analysis_type == "categorical":
            results['analyses']['categorical'] = AnalyticsUtils.run_categorical_analysis(
                df, target_variables
            )
        
        elif analysis_type == "outlier":
            results['analyses']['outlier'] = AnalyticsUtils.run_outlier_analysis(
                df, target_variables
            )
        
        elif analysis_type == "missing":
            results['analyses']['missing_data'] = AnalyticsUtils.run_missing_data_analysis(df)
        
        elif analysis_type == "quality":
            results['analyses']['data_quality'] = AnalyticsUtils.run_data_quality_analysis(df)
        
        elif analysis_type == "correlation":
            results['analyses']['correlation'] = AnalyticsUtils.run_correlation_analysis(df)
        
        elif analysis_type == "text":
            results['analyses']['text'] = AnalyticsUtils.run_basic_text_analysis(
                df, characteristics.get('text_variables', [])
            )
        
        else:
            return AnalyticsUtils.format_api_response(
                'error', 
                None, 
                f'Unknown analysis type: {analysis_type}. Available types: auto, descriptive, basic, comprehensive, distribution, categorical, outlier, missing, temporal, geospatial, quality, correlation, text'
            )
        
        return AnalyticsUtils.format_api_response('success', results)
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, f"{analysis_type} analysis")

@router.post("/project/{project_id}/analyze/basic-statistics")
async def analyze_basic_statistics(
    project_id: str,
    variables: Optional[List[str]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run basic statistical analysis on project data.
    
    Args:
        project_id: Project identifier
        variables: Optional list of variables to analyze
        db: Database session
        
    Returns:
        Basic statistics results
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No data available for analysis'
            )
        
        results = AnalyticsUtils.run_basic_statistics(df, variables)
        
        return AnalyticsUtils.format_api_response('success', {
            'project_id': project_id,
            'analysis_type': 'basic_statistics',
            'results': results
        })
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "basic statistics analysis")

@router.post("/project/{project_id}/analyze/distributions")
async def analyze_distributions(
    project_id: str,
    variables: Optional[List[str]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run distribution analysis on project data.
    
    Args:
        project_id: Project identifier
        variables: Optional list of variables to analyze
        db: Database session
        
    Returns:
        Distribution analysis results
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No data available for analysis'
            )
        
        results = AnalyticsUtils.run_distribution_analysis(df, variables)
        
        return AnalyticsUtils.format_api_response('success', {
            'project_id': project_id,
            'analysis_type': 'distribution_analysis',
            'results': results
        })
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "distribution analysis")

@router.post("/project/{project_id}/analyze/categorical")
async def analyze_categorical_data(
    project_id: str,
    variables: Optional[List[str]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run categorical analysis on project data.
    
    Args:
        project_id: Project identifier
        variables: Optional list of variables to analyze
        db: Database session
        
    Returns:
        Categorical analysis results
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No data available for analysis'
            )
        
        results = AnalyticsUtils.run_categorical_analysis(df, variables)
        
        return AnalyticsUtils.format_api_response('success', {
            'project_id': project_id,
            'analysis_type': 'categorical_analysis',
            'results': results
        })
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "categorical analysis")

@router.post("/project/{project_id}/analyze/outliers")
async def analyze_outliers(
    project_id: str,
    variables: Optional[List[str]] = None,
    methods: Optional[List[str]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run outlier detection analysis on project data.
    
    Args:
        project_id: Project identifier
        variables: Optional list of variables to analyze
        methods: Optional list of outlier detection methods (iqr, zscore, isolation_forest, mad)
        db: Database session
        
    Returns:
        Outlier analysis results
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No data available for analysis'
            )
        
        results = AnalyticsUtils.run_outlier_analysis(df, variables, methods)
        
        return AnalyticsUtils.format_api_response('success', {
            'project_id': project_id,
            'analysis_type': 'outlier_analysis',
            'results': results
        })
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "outlier analysis")

@router.post("/project/{project_id}/analyze/missing-data")
async def analyze_missing_data(
    project_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run missing data analysis on project data.
    
    Args:
        project_id: Project identifier
        db: Database session
        
    Returns:
        Missing data analysis results
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No data available for analysis'
            )
        
        results = AnalyticsUtils.run_missing_data_analysis(df)
        
        return AnalyticsUtils.format_api_response('success', {
            'project_id': project_id,
            'analysis_type': 'missing_data_analysis',
            'results': results
        })
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "missing data analysis")

@router.post("/project/{project_id}/analyze/data-quality")
async def analyze_data_quality(
    project_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run comprehensive data quality analysis on project data.
    
    Args:
        project_id: Project identifier
        db: Database session
        
    Returns:
        Data quality analysis results
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No data available for analysis'
            )
        
        results = AnalyticsUtils.run_data_quality_analysis(df)
        
        return AnalyticsUtils.format_api_response('success', {
            'project_id': project_id,
            'analysis_type': 'data_quality_analysis',
            'results': results
        })
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "data quality analysis")

@router.post("/project/{project_id}/analyze/temporal")
async def analyze_temporal_patterns(
    project_id: str,
    date_column: str,
    value_columns: Optional[List[str]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run temporal pattern analysis on project data.
    
    Args:
        project_id: Project identifier
        date_column: Name of the date/datetime column
        value_columns: Optional list of value columns to analyze over time
        db: Database session
        
    Returns:
        Temporal analysis results
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No data available for analysis'
            )
        
        results = AnalyticsUtils.run_temporal_analysis(df, date_column, value_columns)
        
        return AnalyticsUtils.format_api_response('success', {
            'project_id': project_id,
            'analysis_type': 'temporal_analysis',
            'results': results
        })
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "temporal analysis")

@router.post("/project/{project_id}/analyze/geospatial")
async def analyze_geospatial_patterns(
    project_id: str,
    lat_column: str,
    lon_column: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run geospatial analysis on project data.
    
    Args:
        project_id: Project identifier
        lat_column: Name of the latitude column
        lon_column: Name of the longitude column
        db: Database session
        
    Returns:
        Geospatial analysis results
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No data available for analysis'
            )
        
        results = AnalyticsUtils.run_geospatial_analysis(df, lat_column, lon_column)
        
        return AnalyticsUtils.format_api_response('success', {
            'project_id': project_id,
            'analysis_type': 'geospatial_analysis',
            'results': results
        })
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "geospatial analysis")

@router.post("/project/{project_id}/generate-report")
async def generate_comprehensive_report(
    project_id: str,
    include_plots: bool = False,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate a comprehensive analytics report for project data.
    
    Args:
        project_id: Project identifier
        include_plots: Whether to include plot data in the report
        db: Database session
        
    Returns:
        Comprehensive analytics report
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No data available for report generation'
            )
        
        results = AnalyticsUtils.generate_comprehensive_report(df, include_plots)
        
        return AnalyticsUtils.format_api_response('success', {
            'project_id': project_id,
            'report_type': 'comprehensive_analytics_report',
            'results': results
        })
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "comprehensive report generation")

@router.post("/project/{project_id}/analyze/custom")
async def analyze_custom_data(
    project_id: str,
    data: Dict[str, Any],
    analysis_type: str = "auto",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run analysis on custom data (for testing or external data).
    
    Args:
        project_id: Project identifier (for context)
        data: Custom data as dictionary
        analysis_type: Type of analysis
        db: Database session
        
    Returns:
        Analysis results
    """
    try:
        df = pd.DataFrame(data)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', 
                None, 
                'No data provided for analysis'
            )
        
        characteristics = AnalyticsUtils.analyze_data_characteristics(df)
        
        results = {
            'project_id': project_id,
            'analysis_type': analysis_type,
            'data_characteristics': characteristics,
            'analyses': {}
        }
        
        if analysis_type == "auto":
            results['analyses']['descriptive'] = AnalyticsUtils.run_descriptive_analysis(df)
            
            if len(characteristics.get('numeric_variables', [])) >= 2:
                results['analyses']['correlation'] = AnalyticsUtils.run_correlation_analysis(df)
            
            if len(characteristics.get('text_variables', [])) >= 1:
                results['analyses']['text'] = AnalyticsUtils.run_basic_text_analysis(
                    df, characteristics['text_variables']
                )
        
        elif analysis_type == "descriptive":
            results['analyses']['descriptive'] = AnalyticsUtils.run_descriptive_analysis(df)
        
        elif analysis_type == "correlation":
            results['analyses']['correlation'] = AnalyticsUtils.run_correlation_analysis(df)
        
        elif analysis_type == "text":
            results['analyses']['text'] = AnalyticsUtils.run_basic_text_analysis(
                df, characteristics.get('text_variables', [])
            )
        
        return AnalyticsUtils.format_api_response('success', results)
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, f"custom {analysis_type} analysis")

@router.get("/project/{project_id}/recommendations")
async def get_analysis_recommendations(
    project_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get smart analysis recommendations for a project.
    
    Args:
        project_id: Project identifier
        db: Database session
        
    Returns:
        Analysis recommendations
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', 
                None, 
                'No data available for recommendations'
            )
        
        characteristics = AnalyticsUtils.analyze_data_characteristics(df)
        recommendations = AnalyticsUtils.generate_analysis_recommendations(characteristics)
        
        return AnalyticsUtils.format_api_response('success', {
            'project_id': project_id,
            'recommendations': recommendations,
            'data_summary': {
                'sample_size': characteristics.get('sample_size', 0),
                'variables': characteristics.get('variable_count', 0),
                'data_quality': characteristics.get('completeness_score', 0)
            }
        })
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "recommendations")

@router.get("/analysis-types")
async def get_available_analysis_types() -> Dict[str, Any]:
    """
    Get all available analysis types and methods.
    
    Returns:
        Available analysis types and their descriptions
    """
    try:
        analysis_types = {
            'main_analysis_types': {
                'auto': {
                    'description': 'Automatically runs all applicable analyses based on data characteristics',
                    'includes': ['descriptive', 'correlation', 'text', 'missing_data_if_needed']
                },
                'descriptive': {
                    'description': 'Comprehensive descriptive statistical analysis',
                    'includes': ['basic_statistics', 'distributions', 'correlations', 'outliers', 'missing_analysis']
                },
                'basic': {
                    'description': 'Basic statistical analysis (means, medians, standard deviations)',
                    'includes': ['basic_statistics', 'percentiles']
                },
                'comprehensive': {
                    'description': 'Full comprehensive report with all analyses',
                    'includes': ['comprehensive_report', 'descriptive', 'data_quality']
                },
                'distribution': {
                    'description': 'Distribution analysis for numeric variables',
                    'includes': ['normality_tests', 'skewness_kurtosis', 'outlier_detection']
                },
                'categorical': {
                    'description': 'Categorical variable analysis',
                    'includes': ['frequency_analysis', 'cross_tabulations', 'chi_square_tests']
                },
                'outlier': {
                    'description': 'Outlier detection using multiple methods',
                    'methods': ['iqr', 'zscore', 'isolation_forest', 'mad']
                },
                'missing': {
                    'description': 'Missing data pattern analysis',
                    'includes': ['missing_patterns', 'missing_correlations']
                },
                'temporal': {
                    'description': 'Time-based pattern analysis',
                    'requires': 'date_column',
                    'includes': ['temporal_patterns', 'seasonality', 'time_series_stats']
                },
                'geospatial': {
                    'description': 'Spatial pattern analysis',
                    'requires': ['lat_column', 'lon_column'],
                    'includes': ['spatial_distribution', 'spatial_autocorrelation', 'location_clusters']
                },
                'quality': {
                    'description': 'Data quality assessment',
                    'includes': ['completeness', 'consistency', 'validity']
                },
                'correlation': {
                    'description': 'Correlation analysis between variables',
                    'requires': 'minimum_2_numeric_variables'
                },
                'text': {
                    'description': 'Basic text analysis for text variables',
                    'requires': 'text_variables'
                }
            },
            'specialized_endpoints': {
                '/analyze/basic-statistics': 'Run basic statistical analysis',
                '/analyze/distributions': 'Run distribution analysis',
                '/analyze/categorical': 'Run categorical analysis',
                '/analyze/outliers': 'Run outlier detection',
                '/analyze/missing-data': 'Run missing data analysis',
                '/analyze/data-quality': 'Run data quality analysis',
                '/analyze/temporal': 'Run temporal analysis (requires date_column)',
                '/analyze/geospatial': 'Run geospatial analysis (requires lat/lon columns)',
                '/generate-report': 'Generate comprehensive analytics report'
            },
            'outlier_detection_methods': {
                'iqr': 'Interquartile Range method',
                'zscore': 'Z-score method',
                'isolation_forest': 'Isolation Forest algorithm (for larger datasets)',
                'mad': 'Median Absolute Deviation method'
            }
        }
        
        return AnalyticsUtils.format_api_response('success', analysis_types)
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "getting analysis types")

@router.get("/endpoints")
async def get_analytics_endpoints() -> Dict[str, Any]:
    """
    Get all available analytics endpoints with their descriptions.
    
    Returns:
        List of all analytics endpoints and their functionality
    """
    try:
        endpoints = {
            'project_endpoints': {
                'GET /project/{project_id}/stats': 'Get basic project statistics',
                'GET /project/{project_id}/data-characteristics': 'Get data characteristics and recommendations',
                'GET /project/{project_id}/recommendations': 'Get smart analysis recommendations',
                'POST /project/{project_id}/analyze': 'Run comprehensive analysis with type parameter',
                'POST /project/{project_id}/analyze/basic-statistics': 'Run basic statistical analysis',
                'POST /project/{project_id}/analyze/distributions': 'Run distribution analysis',
                'POST /project/{project_id}/analyze/categorical': 'Run categorical analysis',
                'POST /project/{project_id}/analyze/outliers': 'Run outlier detection',
                'POST /project/{project_id}/analyze/missing-data': 'Run missing data analysis',
                'POST /project/{project_id}/analyze/data-quality': 'Run data quality analysis',
                'POST /project/{project_id}/analyze/temporal': 'Run temporal analysis',
                'POST /project/{project_id}/analyze/geospatial': 'Run geospatial analysis',
                'POST /project/{project_id}/analyze/custom': 'Run analysis on custom data',
                'POST /project/{project_id}/generate-report': 'Generate comprehensive report'
            },
            'utility_endpoints': {
                'GET /analysis-types': 'Get available analysis types and methods',
                'GET /endpoints': 'Get all available endpoints (this endpoint)',
                'GET /health': 'Health check for analytics service'
            },
            'parameters': {
                'analysis_type': {
                    'main_endpoint': '/analyze',
                    'values': ['auto', 'descriptive', 'basic', 'comprehensive', 'distribution', 'categorical', 'outlier', 'missing', 'temporal', 'geospatial', 'quality', 'correlation', 'text'],
                    'default': 'auto'
                },
                'target_variables': {
                    'description': 'Optional list of specific variables to analyze',
                    'applicable_endpoints': ['most analysis endpoints'],
                    'type': 'List[str]'
                },
                'methods': {
                    'endpoint': '/analyze/outliers',
                    'values': ['iqr', 'zscore', 'isolation_forest', 'mad'],
                    'description': 'Outlier detection methods'
                },
                'date_column': {
                    'endpoint': '/analyze/temporal',
                    'description': 'Name of date/datetime column for temporal analysis',
                    'required': True
                },
                'lat_column, lon_column': {
                    'endpoint': '/analyze/geospatial',
                    'description': 'Names of latitude and longitude columns',
                    'required': True
                },
                'include_plots': {
                    'endpoint': '/generate-report',
                    'description': 'Whether to include plot data in reports',
                    'type': 'bool',
                    'default': False
                }
            }
        }
        
        return AnalyticsUtils.format_api_response('success', endpoints)
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "getting endpoints")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the analytics service.
    
    Returns:
        Health status
    """
    try:
        # Test database connection
        conn = AnalyticsUtils.get_django_db_connection()
        conn.close()
        
        return AnalyticsUtils.format_api_response('success', {
            'service': 'analytics',
            'status': 'healthy',
            'database': 'connected',
            'total_endpoints': 15,
            'analysis_types_available': 13,
            'specialized_endpoints': 9
        })
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "health check") 