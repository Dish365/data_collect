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
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run analysis on project data.
    
    Args:
        project_id: Project identifier
        analysis_type: Type of analysis ("auto", "descriptive", "correlation", "text")
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
            # Run all applicable analyses
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
        
        else:
            return AnalyticsUtils.format_api_response(
                'error', 
                None, 
                f'Unknown analysis type: {analysis_type}'
            )
        
        return AnalyticsUtils.format_api_response('success', results)
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, f"{analysis_type} analysis")

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
            'database': 'connected'
        })
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "health check") 