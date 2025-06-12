"""
Inferential analytics endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import pandas as pd

from ....core.database import get_db
from ....analytics.inferential.hypothesis_testing import (
    perform_t_test,
    perform_anova,
    perform_chi_square_test,
    perform_correlation_test
)

router = APIRouter()

@router.post("/t-test")
async def t_test(
    data: Dict[str, List[Any]],
    group_column: str,
    value_column: str,
    alpha: float = 0.05,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform t-test between two groups.
    
    Args:
        data: Dictionary containing the data
        group_column: Column containing group labels
        value_column: Column containing values to test
        alpha: Significance level
        db: Database session
        
    Returns:
        Dictionary with test results
    """
    try:
        df = pd.DataFrame(data)
        groups = df[group_column].unique()
        
        if len(groups) != 2:
            raise HTTPException(
                status_code=400,
                detail="T-test requires exactly two groups"
            )
        
        group1_data = df[df[group_column] == groups[0]][value_column]
        group2_data = df[df[group_column] == groups[1]][value_column]
        
        result = perform_t_test(group1_data, group2_data, alpha)
        result["groups"] = groups.tolist()
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/anova")
async def anova(
    data: Dict[str, List[Any]],
    group_column: str,
    value_column: str,
    alpha: float = 0.05,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform one-way ANOVA test.
    
    Args:
        data: Dictionary containing the data
        group_column: Column containing group labels
        value_column: Column containing values to test
        alpha: Significance level
        db: Database session
        
    Returns:
        Dictionary with test results
    """
    try:
        df = pd.DataFrame(data)
        result = perform_anova(df, group_column, value_column, alpha)
        result["groups"] = df[group_column].unique().tolist()
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/chi-square")
async def chi_square(
    observed: Dict[str, List[Any]],
    expected: Optional[Dict[str, List[Any]]] = None,
    alpha: float = 0.05,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform chi-square test of independence.
    
    Args:
        observed: Observed frequencies
        expected: Expected frequencies (optional)
        alpha: Significance level
        db: Database session
        
    Returns:
        Dictionary with test results
    """
    try:
        observed_df = pd.DataFrame(observed)
        expected_df = pd.DataFrame(expected) if expected else None
        
        return perform_chi_square_test(observed_df, expected_df, alpha)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/correlation")
async def correlation(
    data: Dict[str, List[Any]],
    x_column: str,
    y_column: str,
    method: str = "pearson",
    alpha: float = 0.05,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform correlation test between two variables.
    
    Args:
        data: Dictionary containing the data
        x_column: First variable column
        y_column: Second variable column
        method: Correlation method ('pearson', 'spearman', or 'kendall')
        alpha: Significance level
        db: Database session
        
    Returns:
        Dictionary with test results
    """
    try:
        df = pd.DataFrame(data)
        return perform_correlation_test(df, x_column, y_column, method, alpha)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 