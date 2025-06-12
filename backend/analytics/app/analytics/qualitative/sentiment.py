"""
Sentiment analysis module for qualitative analytics.
"""

from typing import Dict, Any, List
from textblob import TextBlob
import pandas as pd
import numpy as np

def analyze_sentiment(text: str) -> Dict[str, float]:
    """
    Analyze sentiment of text using TextBlob.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with sentiment scores
    """
    blob = TextBlob(text)
    
    return {
        "polarity": float(blob.sentiment.polarity),  # -1 to 1
        "subjectivity": float(blob.sentiment.subjectivity)  # 0 to 1
    }

def analyze_sentiment_batch(texts: List[str]) -> List[Dict[str, float]]:
    """
    Analyze sentiment for a batch of texts.
    
    Args:
        texts: List of input texts
        
    Returns:
        List of sentiment analysis results
    """
    return [analyze_sentiment(text) for text in texts]

def get_sentiment_category(polarity: float) -> str:
    """
    Get sentiment category based on polarity score.
    
    Args:
        polarity: Polarity score (-1 to 1)
        
    Returns:
        Sentiment category
    """
    if polarity > 0.3:
        return "positive"
    elif polarity < -0.3:
        return "negative"
    else:
        return "neutral"

def analyze_sentiment_trends(
    texts: List[str],
    timestamps: List[str]
) -> Dict[str, Any]:
    """
    Analyze sentiment trends over time.
    
    Args:
        texts: List of input texts
        timestamps: List of timestamps corresponding to texts
        
    Returns:
        Dictionary with sentiment trend analysis
    """
    # Convert timestamps to datetime
    df = pd.DataFrame({
        'text': texts,
        'timestamp': pd.to_datetime(timestamps)
    })
    
    # Analyze sentiment for each text
    sentiments = analyze_sentiment_batch(texts)
    df['polarity'] = [s['polarity'] for s in sentiments]
    df['subjectivity'] = [s['subjectivity'] for s in sentiments]
    df['category'] = df['polarity'].apply(get_sentiment_category)
    
    # Calculate daily averages
    daily_avg = df.groupby(df['timestamp'].dt.date).agg({
        'polarity': 'mean',
        'subjectivity': 'mean'
    }).reset_index()
    
    # Calculate category distribution
    category_dist = df['category'].value_counts().to_dict()
    
    return {
        "daily_averages": daily_avg.to_dict('records'),
        "category_distribution": category_dist,
        "overall_sentiment": {
            "mean_polarity": float(df['polarity'].mean()),
            "mean_subjectivity": float(df['subjectivity'].mean())
        }
    }

def analyze_sentiment_by_category(
    texts: List[str],
    categories: List[str]
) -> Dict[str, Dict[str, float]]:
    """
    Analyze sentiment by category.
    
    Args:
        texts: List of input texts
        categories: List of categories corresponding to texts
        
    Returns:
        Dictionary with sentiment analysis by category
    """
    df = pd.DataFrame({
        'text': texts,
        'category': categories
    })
    
    # Analyze sentiment for each text
    sentiments = analyze_sentiment_batch(texts)
    df['polarity'] = [s['polarity'] for s in sentiments]
    df['subjectivity'] = [s['subjectivity'] for s in sentiments]
    
    # Calculate statistics by category
    category_stats = df.groupby('category').agg({
        'polarity': ['mean', 'std', 'count'],
        'subjectivity': ['mean', 'std']
    }).to_dict()
    
    return {
        category: {
            "mean_polarity": float(stats['polarity']['mean']),
            "std_polarity": float(stats['polarity']['std']),
            "mean_subjectivity": float(stats['subjectivity']['mean']),
            "std_subjectivity": float(stats['subjectivity']['std']),
            "count": int(stats['polarity']['count'])
        }
        for category, stats in category_stats.items()
    } 