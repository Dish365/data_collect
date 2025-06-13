"""
Auto-detection endpoints for data analysis.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import pandas as pd

from core.database import get_db
from app.analytics.auto_detect.detector import (
    detect_data_type,
    detect_analysis_type,
    suggest_visualizations,
    detect_anomalies
)

router = APIRouter()

@router.post("/data-types")
async def analyze_data_types(
    data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Detect data types of columns in the input data.
    
    Args:
        data: Input data as a dictionary
        db: Database session
        
    Returns:
        Dictionary mapping column names to detected types
    """
    try:
        df = pd.DataFrame(data)
        return detect_data_type(df)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error analyzing data types: {str(e)}"
        )

@router.post("/distribution/{column}")
async def analyze_distribution(
    column: str,
    data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Detect the distribution of a numeric column.
    
    Args:
        column: Column to analyze
        data: Input data as a dictionary
        db: Database session
        
    Returns:
        Dictionary with distribution information
    """
    try:
        df = pd.DataFrame(data)
        if column not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Column {column} not found in data"
            )
        return detect_analysis_type(df, column)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error analyzing distribution: {str(e)}"
        )

@router.post("/correlations")
async def analyze_correlations(
    data: Dict[str, Any],
    threshold: float = 0.5,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Detect significant correlations between numeric columns.
    
    Args:
        data: Input data as a dictionary
        threshold: Correlation threshold
        db: Database session
        
    Returns:
        List of significant correlations
    """
    try:
        df = pd.DataFrame(data)
        return detect_anomalies(df, threshold)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error analyzing correlations: {str(e)}"
        )

@router.post("/clusters")
async def analyze_clusters(
    data: Dict[str, Any],
    max_clusters: int = 5,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Detect natural clusters in numeric data.
    
    Args:
        data: Input data as a dictionary
        max_clusters: Maximum number of clusters to try
        db: Database session
        
    Returns:
        Dictionary with clustering information
    """
    try:
        df = pd.DataFrame(data)
        return suggest_visualizations(df, max_clusters)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error analyzing clusters: {str(e)}"
        )

@router.post("/suggest")
async def get_analysis_suggestions(
    data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, List[str]]:
    """
    Suggest appropriate analyses based on data characteristics.
    
    Args:
        data: Input data as a dictionary
        db: Database session
        
    Returns:
        Dictionary with suggested analyses
    """
    try:
        df = pd.DataFrame(data)
        return suggest_visualizations(df)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error suggesting analyses: {str(e)}"
        ) 