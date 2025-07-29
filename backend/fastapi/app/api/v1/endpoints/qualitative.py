"""
Qualitative Analytics Endpoints
Handles text analysis, sentiment analysis, thematic analysis, and qualitative research methods.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import pandas as pd
from asgiref.sync import sync_to_async

from core.database import get_db
from app.utils.shared import AnalyticsUtils

router = APIRouter()

@router.post("/project/{project_id}/analyze/text")
async def analyze_text_data(
    project_id: str,
    text_fields: Optional[List[str]] = None,
    analysis_type: str = "comprehensive",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run comprehensive text analysis on project data.
    
    Args:
        project_id: Project identifier
        text_fields: Optional list of text fields to analyze
        analysis_type: Type of text analysis (basic, comprehensive, sentiment, themes)
        db: Database session
        
    Returns:
        Text analysis results
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No data available for analysis'
            )
        
        # Get data characteristics to identify text variables if not specified
        characteristics = AnalyticsUtils.analyze_data_characteristics(df)
        
        if not text_fields:
            text_fields = characteristics.get('text_variables', [])
        
        if not text_fields:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No text variables found in the data'
            )
        
        results = AnalyticsUtils.run_basic_text_analysis(df, text_fields)
        
        return AnalyticsUtils.format_api_response('success', {
            'project_id': project_id,
            'analysis_type': 'text_analysis',
            'text_fields_analyzed': text_fields,
            'results': results
        })
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "text analysis")

@router.post("/project/{project_id}/analyze/sentiment")
async def analyze_sentiment(
    project_id: str,
    text_fields: Optional[List[str]] = None,
    sentiment_method: str = "vader",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run sentiment analysis on text data.
    
    Args:
        project_id: Project identifier
        text_fields: Optional list of text fields to analyze
        sentiment_method: Sentiment analysis method (vader, textblob)
        db: Database session
        
    Returns:
        Sentiment analysis results
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No data available for analysis'
            )
        
        # Get data characteristics to identify text variables if not specified
        characteristics = AnalyticsUtils.analyze_data_characteristics(df)
        
        if not text_fields:
            text_fields = characteristics.get('text_variables', [])
        
        if not text_fields:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No text variables found in the data'
            )
        
        results = AnalyticsUtils.run_sentiment_analysis(df, text_fields, sentiment_method)
        
        return AnalyticsUtils.format_api_response('success', {
            'project_id': project_id,
            'analysis_type': 'sentiment_analysis',
            'text_fields_analyzed': text_fields,
            'sentiment_method': sentiment_method,
            'results': results
        })
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "sentiment analysis")

@router.post("/project/{project_id}/analyze/themes")
async def analyze_themes(
    project_id: str,
    text_fields: Optional[List[str]] = None,
    num_themes: int = 5,
    theme_method: str = "lda",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run thematic analysis on text data.
    
    Args:
        project_id: Project identifier
        text_fields: Optional list of text fields to analyze
        num_themes: Number of themes to extract
        theme_method: Thematic analysis method (lda, nmf, clustering)
        db: Database session
        
    Returns:
        Thematic analysis results
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No data available for analysis'
            )
        
        # Get data characteristics to identify text variables if not specified
        characteristics = AnalyticsUtils.analyze_data_characteristics(df)
        
        if not text_fields:
            text_fields = characteristics.get('text_variables', [])
        
        if not text_fields:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No text variables found in the data'
            )
        
        results = AnalyticsUtils.run_theme_analysis(df, text_fields, num_themes, theme_method)
        
        return AnalyticsUtils.format_api_response('success', {
            'project_id': project_id,
            'analysis_type': 'theme_analysis',
            'text_fields_analyzed': text_fields,
            'num_themes': num_themes,
            'theme_method': theme_method,
            'results': results
        })
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "theme analysis")

@router.post("/project/{project_id}/analyze/word-frequency")
async def analyze_word_frequency(
    project_id: str,
    text_fields: Optional[List[str]] = None,
    top_n: int = 50,
    min_word_length: int = 3,
    remove_stopwords: bool = True,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run word frequency analysis on text data.
    
    Args:
        project_id: Project identifier
        text_fields: Optional list of text fields to analyze
        top_n: Number of top words to return
        min_word_length: Minimum word length to include
        remove_stopwords: Whether to remove common stopwords
        db: Database session
        
    Returns:
        Word frequency analysis results
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No data available for analysis'
            )
        
        # Get data characteristics to identify text variables if not specified
        characteristics = AnalyticsUtils.analyze_data_characteristics(df)
        
        if not text_fields:
            text_fields = characteristics.get('text_variables', [])
        
        if not text_fields:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No text variables found in the data'
            )
        
        results = AnalyticsUtils.run_word_frequency_analysis(
            df, text_fields, top_n, min_word_length, remove_stopwords
        )
        
        return AnalyticsUtils.format_api_response('success', {
            'project_id': project_id,
            'analysis_type': 'word_frequency_analysis',
            'text_fields_analyzed': text_fields,
            'parameters': {
                'top_n': top_n,
                'min_word_length': min_word_length,
                'remove_stopwords': remove_stopwords
            },
            'results': results
        })
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "word frequency analysis")

@router.post("/project/{project_id}/analyze/content-analysis")
async def analyze_content(
    project_id: str,
    text_fields: Optional[List[str]] = None,
    analysis_framework: str = "inductive",
    coding_scheme: Optional[Dict[str, List[str]]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run content analysis on text data using specified framework.
    
    Args:
        project_id: Project identifier
        text_fields: Optional list of text fields to analyze
        analysis_framework: Content analysis framework (inductive, deductive, mixed)
        coding_scheme: Optional predefined coding scheme for deductive analysis
        db: Database session
        
    Returns:
        Content analysis results
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No data available for analysis'
            )
        
        # Get data characteristics to identify text variables if not specified
        characteristics = AnalyticsUtils.analyze_data_characteristics(df)
        
        if not text_fields:
            text_fields = characteristics.get('text_variables', [])
        
        if not text_fields:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No text variables found in the data'
            )
        
        results = AnalyticsUtils.run_content_analysis(
            df, text_fields, analysis_framework, coding_scheme
        )
        
        return AnalyticsUtils.format_api_response('success', {
            'project_id': project_id,
            'analysis_type': 'content_analysis',
            'text_fields_analyzed': text_fields,
            'analysis_framework': analysis_framework,
            'coding_scheme_used': coding_scheme is not None,
            'results': results
        })
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "content analysis")

@router.post("/project/{project_id}/analyze/qualitative-coding") 
async def analyze_qualitative_coding(
    project_id: str,
    text_fields: Optional[List[str]] = None,
    coding_method: str = "open",
    auto_code: bool = True,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Run qualitative coding analysis on text data.
    
    Args:
        project_id: Project identifier
        text_fields: Optional list of text fields to analyze
        coding_method: Coding method (open, axial, selective)
        auto_code: Whether to use automated coding assistance
        db: Database session
        
    Returns:
        Qualitative coding results
    """
    try:
        df = await AnalyticsUtils.get_project_data(project_id)
        
        if df.empty:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No data available for analysis'
            )
        
        # Get data characteristics to identify text variables if not specified
        characteristics = AnalyticsUtils.analyze_data_characteristics(df)
        
        if not text_fields:
            text_fields = characteristics.get('text_variables', [])
        
        if not text_fields:
            return AnalyticsUtils.format_api_response(
                'error', None, 'No text variables found in the data'
            )
        
        results = AnalyticsUtils.run_qualitative_coding(
            df, text_fields, coding_method, auto_code
        )
        
        return AnalyticsUtils.format_api_response('success', {
            'project_id': project_id,
            'analysis_type': 'qualitative_coding',
            'text_fields_analyzed': text_fields,
            'coding_method': coding_method,
            'auto_code_enabled': auto_code,
            'results': results
        })
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "qualitative coding analysis")

@router.get("/analysis-types")
async def get_qualitative_analysis_types() -> Dict[str, Any]:
    """
    Get available qualitative analysis types and methods.
    
    Returns:
        Available qualitative analysis types
    """
    try:
        analysis_types = {
            'qualitative_analysis_types': {
                'text_analysis': {
                    'description': 'Comprehensive text analysis including basic statistics and patterns',
                    'includes': ['word_count', 'readability', 'basic_patterns', 'text_statistics']
                },
                'sentiment_analysis': {
                    'description': 'Sentiment analysis using various methods',
                    'methods': ['vader', 'textblob', 'custom'],
                    'includes': ['sentiment_scores', 'emotion_detection', 'polarity_analysis']
                },
                'theme_analysis': {
                    'description': 'Thematic analysis and topic modeling',
                    'methods': ['lda', 'nmf', 'clustering', 'manual'],
                    'includes': ['topic_extraction', 'theme_identification', 'conceptual_mapping']
                },
                'word_frequency': {
                    'description': 'Word frequency and lexical analysis',
                    'includes': ['frequency_counts', 'tf_idf', 'n_gram_analysis', 'vocabulary_analysis']
                },
                'content_analysis': {
                    'description': 'Systematic content analysis using various frameworks',
                    'frameworks': ['inductive', 'deductive', 'mixed'],
                    'includes': ['category_development', 'pattern_identification', 'systematic_coding']
                },
                'qualitative_coding': {
                    'description': 'Qualitative data coding and analysis',
                    'methods': ['open', 'axial', 'selective'],
                    'includes': ['code_development', 'category_formation', 'theoretical_integration']
                }
            },
            'text_analysis_methods': {
                'sentiment_methods': ['vader', 'textblob', 'custom'],
                'theme_methods': ['lda', 'nmf', 'clustering', 'manual'],
                'coding_methods': ['open', 'axial', 'selective'],
                'content_frameworks': ['inductive', 'deductive', 'mixed']
            }
        }
        
        return AnalyticsUtils.format_api_response('success', analysis_types)
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "getting qualitative analysis types")

@router.get("/endpoints")
async def get_qualitative_endpoints() -> Dict[str, Any]:
    """
    Get all available qualitative analytics endpoints.
    
    Returns:
        List of all qualitative analytics endpoints
    """
    try:
        endpoints = {
            'qualitative_analytics_endpoints': {
                'POST /project/{project_id}/analyze/text': 'Run comprehensive text analysis',
                'POST /project/{project_id}/analyze/sentiment': 'Run sentiment analysis',
                'POST /project/{project_id}/analyze/themes': 'Run thematic analysis',
                'POST /project/{project_id}/analyze/word-frequency': 'Run word frequency analysis',
                'POST /project/{project_id}/analyze/content-analysis': 'Run content analysis',
                'POST /project/{project_id}/analyze/qualitative-coding': 'Run qualitative coding analysis',
                'GET /analysis-types': 'Get available qualitative analysis types',
                'GET /endpoints': 'Get all qualitative analytics endpoints'
            },
            'parameters': {
                'text_fields': {
                    'description': 'Optional list of text fields to analyze',
                    'type': 'List[str]',
                    'applicable_endpoints': 'all'
                },
                'sentiment_method': {
                    'values': ['vader', 'textblob', 'custom'],
                    'default': 'vader',
                    'endpoint': '/analyze/sentiment'
                },
                'num_themes': {
                    'description': 'Number of themes to extract',
                    'type': 'int',
                    'default': 5,
                    'endpoint': '/analyze/themes'
                },
                'theme_method': {
                    'values': ['lda', 'nmf', 'clustering', 'manual'],
                    'default': 'lda',
                    'endpoint': '/analyze/themes'
                },
                'coding_method': {
                    'values': ['open', 'axial', 'selective'],
                    'default': 'open',
                    'endpoint': '/analyze/qualitative-coding'
                },
                'analysis_framework': {
                    'values': ['inductive', 'deductive', 'mixed'],
                    'default': 'inductive',
                    'endpoint': '/analyze/content-analysis'
                }
            }
        }
        
        return AnalyticsUtils.format_api_response('success', endpoints)
        
    except Exception as e:
        return AnalyticsUtils.handle_analysis_error(e, "getting qualitative endpoints") 