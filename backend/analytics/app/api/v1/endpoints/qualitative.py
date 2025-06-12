"""
Qualitative analytics endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import pandas as pd

from ....core.database import get_db
from ....analytics.qualitative.text_analysis import (
    analyze_text_frequency,
    analyze_text_similarity,
    extract_key_phrases,
    analyze_text_patterns
)
from ....analytics.qualitative.sentiment import (
    analyze_sentiment,
    analyze_sentiment_batch,
    analyze_sentiment_trends,
    analyze_sentiment_by_category
)

router = APIRouter()

@router.post("/text/frequency")
async def text_frequency(
    text: str,
    db: Session = Depends(get_db)
) -> Dict[str, int]:
    """
    Analyze word frequency in text.
    
    Args:
        text: Input text
        db: Database session
        
    Returns:
        Dictionary of word frequencies
    """
    try:
        return analyze_text_frequency(text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/text/similarity")
async def text_similarity(
    text1: str,
    text2: str,
    db: Session = Depends(get_db)
) -> Dict[str, float]:
    """
    Calculate similarity between two texts.
    
    Args:
        text1: First text
        text2: Second text
        db: Database session
        
    Returns:
        Dictionary with similarity score
    """
    try:
        similarity = analyze_text_similarity(text1, text2)
        return {"similarity": similarity}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/text/patterns")
async def text_patterns(
    text: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze patterns in text.
    
    Args:
        text: Input text
        db: Database session
        
    Returns:
        Dictionary with pattern analysis results
    """
    try:
        return analyze_text_patterns(text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sentiment")
async def sentiment(
    text: str,
    db: Session = Depends(get_db)
) -> Dict[str, float]:
    """
    Analyze sentiment of text.
    
    Args:
        text: Input text
        db: Database session
        
    Returns:
        Dictionary with sentiment scores
    """
    try:
        return analyze_sentiment(text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sentiment/batch")
async def sentiment_batch(
    texts: List[str],
    db: Session = Depends(get_db)
) -> List[Dict[str, float]]:
    """
    Analyze sentiment for multiple texts.
    
    Args:
        texts: List of input texts
        db: Database session
        
    Returns:
        List of sentiment analysis results
    """
    try:
        return analyze_sentiment_batch(texts)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sentiment/trends")
async def sentiment_trends(
    texts: List[str],
    timestamps: List[str],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze sentiment trends over time.
    
    Args:
        texts: List of input texts
        timestamps: List of timestamps corresponding to texts
        db: Database session
        
    Returns:
        Dictionary with sentiment trend analysis
    """
    try:
        return analyze_sentiment_trends(texts, timestamps)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sentiment/by-category")
async def sentiment_by_category(
    texts: List[str],
    categories: List[str],
    db: Session = Depends(get_db)
) -> Dict[str, Dict[str, float]]:
    """
    Analyze sentiment by category.
    
    Args:
        texts: List of input texts
        categories: List of categories corresponding to texts
        db: Database session
        
    Returns:
        Dictionary with sentiment analysis by category
    """
    try:
        return analyze_sentiment_by_category(texts, categories)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 