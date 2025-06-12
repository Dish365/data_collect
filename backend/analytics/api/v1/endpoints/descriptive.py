"""
Descriptive analytics endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import pandas as pd
import numpy as np

from ....core.database import get_db
from ....analytics.descriptive import statistics

router = APIRouter()

@router.post("/basic-stats")
async def get_basic_statistics(
    data: Dict[str, List[Any]],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Calculate basic descriptive statistics for numerical data.
    
    Args:
        data: Dictionary containing lists of numerical data
        db: Database session
    
    Returns:
        Dictionary containing basic statistics for each numerical column
    """
    try:
        # Convert input data to pandas DataFrame
        df = pd.DataFrame(data)
        
        # Calculate basic statistics
        stats = {
            column: {
                "mean": float(df[column].mean()),
                "median": float(df[column].median()),
                "std": float(df[column].std()),
                "min": float(df[column].min()),
                "max": float(df[column].max()),
                "count": int(df[column].count())
            }
            for column in df.select_dtypes(include=[np.number]).columns
        }
        
        return {"statistics": stats}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 