"""
Qualitative analytics endpoints with auto-detection capabilities.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import pandas as pd
import json

from core.database import get_db
from app.analytics.qualitative.auto_detection import (
    QualitativeAutoDetector,
    auto_analyze
)
from app.analytics.auto_detect.base_detector import DataType

router = APIRouter()

@router.post("/analyze")
async def analyze_qualitative(
    data: Dict[str, Any],
    text_columns: Optional[List[str]] = None,
    research_goals: Optional[List[str]] = None,
    metadata: Optional[List[Dict[str, Any]]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform comprehensive qualitative analysis with auto-detection.
    
    Args:
        data: Input data as a dictionary
        text_columns: Specific text columns to analyze
        research_goals: Optional research objectives
        metadata: Optional metadata about the text data
        db: Database session
        
    Returns:
        Comprehensive qualitative analysis results
    """
    try:
        df = pd.DataFrame(data)
        
        # Extract text data
        texts = _extract_text_data(df, text_columns)
        
        if not texts:
            raise HTTPException(
                status_code=400,
                detail="No text data found for qualitative analysis"
            )
        
        # Use the auto-analysis function
        results = auto_analyze(
            texts,
            metadata=metadata,
            research_goals=research_goals
        )
        
        # Format for API response
        return {
            "status": "success",
            "analysis_type": "qualitative",
            "data_overview": _format_text_overview(results["data_detection"]),
            "method_recommendations": _format_method_suggestions(results["method_suggestions"]),
            "recommended_workflow": results["recommended_workflow"],
            "analysis_summary": results["analysis_summary"],
            "text_characteristics": _get_detailed_text_characteristics(texts)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error in qualitative analysis: {str(e)}"
        )

@router.post("/suggest-methods")
async def suggest_qualitative_methods(
    data: Dict[str, Any],
    text_columns: Optional[List[str]] = None,
    research_goals: Optional[List[str]] = None,
    metadata: Optional[List[Dict[str, Any]]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get method suggestions for qualitative analysis.
    
    Args:
        data: Input data as a dictionary
        text_columns: Specific text columns to analyze
        research_goals: Optional research objectives
        metadata: Optional metadata about the text data
        db: Database session
        
    Returns:
        Method suggestions and recommendations
    """
    try:
        df = pd.DataFrame(data)
        detector = QualitativeAutoDetector()
        
        # Extract text data
        texts = _extract_text_data(df, text_columns)
        
        if not texts:
            return {
                "status": "error",
                "message": "No text data found for analysis",
                "suggestions": []
            }
        
        suggestions = detector.suggest_analyses(df, texts=texts, analysis_goals=research_goals)
        
        return {
            "status": "success",
            "text_characteristics": _format_text_characteristics(texts),
            "primary_recommendations": [_format_recommendation(rec) for rec in suggestions.primary_recommendations],
            "secondary_recommendations": [_format_recommendation(rec) for rec in suggestions.secondary_recommendations],
            "optional_analyses": [_format_recommendation(rec) for rec in suggestions.optional_analyses],
            "data_quality_warnings": suggestions.data_quality_warnings,
            "analysis_order": suggestions.analysis_order
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error suggesting methods: {str(e)}"
        )

@router.post("/configure-method/{method_name}")
async def configure_qualitative_method(
    method_name: str,
    data: Dict[str, Any],
    text_columns: Optional[List[str]] = None,
    metadata: Optional[List[Dict[str, Any]]] = None,
    custom_parameters: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Auto-configure parameters for a specific qualitative analysis method.
    
    Args:
        method_name: Name of the analysis method
        data: Input data as a dictionary
        text_columns: Specific text columns to analyze
        metadata: Optional metadata about the text data
        custom_parameters: Optional custom parameter overrides
        db: Database session
        
    Returns:
        Optimized configuration for the method
    """
    try:
        df = pd.DataFrame(data)
        detector = QualitativeAutoDetector()
        
        # Extract text data
        texts = _extract_text_data(df, text_columns)
        
        if not texts:
            raise HTTPException(
                status_code=400,
                detail="No text data found for configuration"
            )
        
        config = detector.auto_configure_analysis(
            texts,
            method_name,
            metadata=metadata
        )
        
        # Apply custom parameter overrides
        if custom_parameters:
            config.update(custom_parameters)
        
        return {
            "method": method_name,
            "configuration": config,
            "parameter_explanation": _explain_qualitative_parameters(method_name, config),
            "execution_guidance": _get_qualitative_execution_guidance(method_name, config),
            "text_requirements": _get_text_requirements(method_name)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error configuring method {method_name}: {str(e)}"
        )

@router.post("/detect-data-type")
async def detect_qualitative_data_type(
    data: Dict[str, Any],
    text_columns: Optional[List[str]] = None,
    metadata: Optional[List[Dict[str, Any]]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Detect the type and characteristics of qualitative data.
    
    Args:
        data: Input data as a dictionary
        text_columns: Specific text columns to analyze
        metadata: Optional metadata about the text data
        db: Database session
        
    Returns:
        Data type detection results
    """
    try:
        df = pd.DataFrame(data)
        detector = QualitativeAutoDetector()
        
        # Extract text data
        texts = _extract_text_data(df, text_columns)
        
        if not texts:
            return {
                "status": "error",
                "message": "No text data found for type detection"
            }
        
        type_detection = detector.detect_data_type(texts, metadata)
        
        return {
            "status": "success",
            "primary_data_type": type_detection["primary_data_type"],
            "confidence": type_detection["confidence"],
            "data_characteristics": type_detection["data_characteristics"],
            "detected_patterns": type_detection["detected_patterns"],
            "data_type_scores": type_detection["data_type_scores"],
            "recommendations": _get_type_based_recommendations(type_detection)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error detecting data type: {str(e)}"
        )

@router.post("/text-characteristics")
async def get_text_characteristics(
    data: Dict[str, Any],
    text_columns: Optional[List[str]] = None,
    include_linguistic_features: bool = True,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed characteristics of text data.
    
    Args:
        data: Input data as a dictionary
        text_columns: Specific text columns to analyze
        include_linguistic_features: Whether to include advanced linguistic analysis
        db: Database session
        
    Returns:
        Detailed text characteristics
    """
    try:
        df = pd.DataFrame(data)
        
        # Extract text data
        texts = _extract_text_data(df, text_columns)
        
        if not texts:
            return {
                "status": "error",
                "message": "No text data found for analysis"
            }
        
        characteristics = _analyze_text_characteristics(texts, include_linguistic_features)
        
        return {
            "status": "success",
            "text_characteristics": characteristics,
            "analysis_suitability": _assess_text_suitability(characteristics),
            "preprocessing_recommendations": _get_preprocessing_recommendations(characteristics)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error analyzing text characteristics: {str(e)}"
        )

@router.post("/quick-recommendation")
async def get_quick_qualitative_recommendation(
    texts: List[str],
    analysis_focus: str = "auto",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get quick analysis recommendation for qualitative data.
    
    Args:
        texts: List of text documents
        analysis_focus: Focus area ('auto', 'sentiment', 'themes', 'content')
        db: Database session
        
    Returns:
        Quick recommendation with rationale
    """
    try:
        if not texts:
            raise HTTPException(
                status_code=400,
                detail="No texts provided for analysis"
            )
        
        detector = QualitativeAutoDetector()
        
        # Get quick recommendation based on focus
        if analysis_focus == "auto":
            # Use suggest_analyses for automatic recommendation
            suggestions = detector.suggest_analyses(pd.DataFrame({'text': texts}), texts=texts)
            recommendation = suggestions.primary_recommendations[0].method if suggestions.primary_recommendations else "content_analysis"
        else:
            # Map focus to specific method
            focus_mapping = {
                "sentiment": "sentiment_analysis",
                "themes": "thematic_analysis",
                "content": "content_analysis",
                "coding": "coding"
            }
            recommendation = focus_mapping.get(analysis_focus, "content_analysis")
        
        return {
            "status": "success",
            "recommendation": recommendation,
            "rationale": _get_recommendation_rationale(texts, recommendation, analysis_focus),
            "estimated_time": _estimate_qualitative_analysis_time(recommendation, len(texts)),
            "next_steps": _get_qualitative_next_steps(recommendation),
            "text_info": _get_text_summary(texts)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error getting quick recommendation: {str(e)}"
        )

@router.get("/methods")
async def list_qualitative_methods(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    List all available qualitative analysis methods.
    
    Returns:
        Dictionary of available methods with requirements
    """
    try:
        detector = QualitativeAutoDetector()
        methods = detector.get_method_requirements()
        
        return {
            "status": "success",
            "methods": methods,
            "method_categories": _categorize_qualitative_methods(methods),
            "text_type_guide": _get_text_type_guide(),
            "usage_guidelines": _get_qualitative_usage_guidelines()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing methods: {str(e)}"
        )

@router.post("/generate-report")
async def generate_qualitative_report(
    data: Dict[str, Any],
    text_columns: Optional[List[str]] = None,
    research_goals: Optional[List[str]] = None,
    include_examples: bool = True,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate a comprehensive qualitative analysis report.
    
    Args:
        data: Input data as a dictionary
        text_columns: Specific text columns to analyze
        research_goals: Optional research objectives
        include_examples: Whether to include text examples
        db: Database session
        
    Returns:
        Comprehensive analysis report
    """
    try:
        df = pd.DataFrame(data)
        
        # Extract text data
        texts = _extract_text_data(df, text_columns)
        
        if not texts:
            raise HTTPException(
                status_code=400,
                detail="No text data found for report generation"
            )
        
        # Generate comprehensive analysis
        results = auto_analyze(texts, research_goals=research_goals)
        
        response = {
            "status": "success",
            "report": _generate_text_report(results, texts),
            "metadata": {
                "generated_at": pd.Timestamp.now().isoformat(),
                "text_count": len(texts),
                "analysis_type": "qualitative",
                "data_type": results["data_detection"]["primary_data_type"]
            }
        }
        
        if include_examples:
            response["text_examples"] = _get_representative_examples(texts)
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error generating report: {str(e)}"
        )

# Helper functions for qualitative analytics endpoints

def _extract_text_data(df: pd.DataFrame, text_columns: Optional[List[str]] = None) -> List[str]:
    """Extract text data from DataFrame."""
    texts = []
    
    if text_columns:
        # Use specified columns
        for col in text_columns:
            if col in df.columns:
                col_texts = df[col].dropna().astype(str).tolist()
                texts.extend(col_texts)
    else:
        # Auto-detect text columns
        for col in df.columns:
            if df[col].dtype == 'object':  # Potential text column
                try:
                    # Check if it's substantial text (average length > 20 chars)
                    avg_length = df[col].str.len().mean()
                    if avg_length > 20:
                        col_texts = df[col].dropna().astype(str).tolist()
                        texts.extend(col_texts)
                except:
                    continue
    
    return [text for text in texts if text.strip()]  # Remove empty texts

def _format_text_overview(data_detection: Dict[str, Any]) -> Dict[str, Any]:
    """Format text data overview for API response."""
    return {
        "primary_data_type": data_detection["primary_data_type"],
        "confidence": data_detection["confidence"],
        "text_count": data_detection["data_characteristics"]["num_texts"],
        "average_words_per_text": data_detection["data_characteristics"]["avg_words_per_text"],
        "lexical_diversity": data_detection["data_characteristics"]["lexical_diversity"],
        "total_words": data_detection["data_characteristics"]["total_words"]
    }

def _format_method_suggestions(suggestions: Dict[str, Any]) -> Dict[str, Any]:
    """Format method suggestions for API response."""
    return {
        "primary_recommendations": suggestions["primary_recommendations"],
        "secondary_recommendations": suggestions["secondary_recommendations"],
        "not_recommended": suggestions["not_recommended"],
        "analysis_rationale": suggestions.get("analysis_rationale", {}),
        "parameter_suggestions": suggestions.get("parameter_suggestions", {})
    }

def _format_text_characteristics(texts: List[str]) -> Dict[str, Any]:
    """Format basic text characteristics."""
    if not texts:
        return {"error": "No texts provided"}
    
    word_counts = [len(text.split()) for text in texts]
    
    return {
        "text_count": len(texts),
        "total_words": sum(word_counts),
        "average_words": sum(word_counts) / len(word_counts),
        "median_words": sorted(word_counts)[len(word_counts) // 2],
        "min_words": min(word_counts),
        "max_words": max(word_counts),
        "average_chars": sum(len(text) for text in texts) / len(texts)
    }

def _format_recommendation(rec) -> Dict[str, Any]:
    """Format a single recommendation for API response."""
    return {
        "method": rec.method,
        "score": rec.score,
        "confidence": rec.confidence.value,
        "rationale": rec.rationale,
        "estimated_time": rec.estimated_time,
        "function_call": rec.function_call,
        "parameters": rec.parameters
    }

def _get_detailed_text_characteristics(texts: List[str]) -> Dict[str, Any]:
    """Get detailed characteristics of text data."""
    if not texts:
        return {"error": "No texts provided"}
    
    import re
    from collections import Counter
    
    # Basic statistics
    word_counts = [len(text.split()) for text in texts]
    char_counts = [len(text) for text in texts]
    
    # Word analysis
    all_words = []
    for text in texts:
        words = re.findall(r'\b\w+\b', text.lower())
        all_words.extend(words)
    
    word_freq = Counter(all_words)
    
    return {
        "text_statistics": {
            "count": len(texts),
            "total_words": sum(word_counts),
            "unique_words": len(set(all_words)),
            "average_words": sum(word_counts) / len(word_counts),
            "average_chars": sum(char_counts) / len(char_counts),
            "lexical_diversity": len(set(all_words)) / len(all_words) if all_words else 0
        },
        "content_patterns": {
            "most_common_words": dict(word_freq.most_common(10)),
            "text_length_distribution": {
                "min": min(word_counts),
                "max": max(word_counts),
                "median": sorted(word_counts)[len(word_counts) // 2],
                "std": (sum((x - sum(word_counts)/len(word_counts))**2 for x in word_counts) / len(word_counts))**0.5
            }
        }
    }

def _analyze_text_characteristics(texts: List[str], include_linguistic: bool = True) -> Dict[str, Any]:
    """Perform comprehensive text analysis."""
    characteristics = _get_detailed_text_characteristics(texts)
    
    if include_linguistic:
        characteristics["linguistic_features"] = _extract_linguistic_features(texts)
    
    characteristics["readability"] = _assess_text_readability(texts)
    characteristics["content_types"] = _identify_content_types(texts)
    
    return characteristics

def _extract_linguistic_features(texts: List[str]) -> Dict[str, Any]:
    """Extract linguistic features from texts."""
    import re
    
    features = {
        "punctuation_usage": {},
        "sentence_patterns": {},
        "question_indicators": 0,
        "emotional_indicators": 0
    }
    
    # Analyze punctuation
    punct_counts = {"periods": 0, "questions": 0, "exclamations": 0}
    
    for text in texts:
        punct_counts["periods"] += text.count('.')
        punct_counts["questions"] += text.count('?')
        punct_counts["exclamations"] += text.count('!')
        
        # Check for question indicators
        if any(q_word in text.lower() for q_word in ['what', 'how', 'why', 'when', 'where', 'who']):
            features["question_indicators"] += 1
            
        # Check for emotional indicators
        emotional_words = ['feel', 'think', 'believe', 'love', 'hate', 'excited', 'worried']
        if any(em_word in text.lower() for em_word in emotional_words):
            features["emotional_indicators"] += 1
    
    features["punctuation_usage"] = punct_counts
    
    return features

def _assess_text_readability(texts: List[str]) -> Dict[str, Any]:
    """Assess text readability and complexity."""
    word_counts = [len(text.split()) for text in texts]
    sentence_counts = [text.count('.') + text.count('!') + text.count('?') + 1 for text in texts]
    
    avg_words_per_sentence = sum(word_counts) / sum(sentence_counts) if sum(sentence_counts) > 0 else 0
    
    return {
        "average_words_per_sentence": avg_words_per_sentence,
        "complexity_level": "high" if avg_words_per_sentence > 20 else "medium" if avg_words_per_sentence > 10 else "low",
        "text_density": "dense" if sum(word_counts) / len(texts) > 50 else "moderate"
    }

def _identify_content_types(texts: List[str]) -> Dict[str, int]:
    """Identify types of content in texts."""
    content_types = {
        "narrative": 0,
        "descriptive": 0,
        "opinion": 0,
        "factual": 0,
        "question_response": 0
    }
    
    for text in texts:
        text_lower = text.lower()
        
        # Narrative indicators
        if any(word in text_lower for word in ['story', 'happened', 'then', 'after', 'before']):
            content_types["narrative"] += 1
            
        # Opinion indicators
        if any(word in text_lower for word in ['think', 'believe', 'opinion', 'feel', 'should']):
            content_types["opinion"] += 1
            
        # Question response indicators
        if any(word in text_lower for word in ['answer', 'response', 'question']):
            content_types["question_response"] += 1
            
        # Default to descriptive if no clear type
        if not any([
            any(word in text_lower for word in ['story', 'happened', 'then']),
            any(word in text_lower for word in ['think', 'believe', 'opinion']),
            any(word in text_lower for word in ['answer', 'response', 'question'])
        ]):
            content_types["descriptive"] += 1
    
    return content_types

def _assess_text_suitability(characteristics: Dict[str, Any]) -> Dict[str, Any]:
    """Assess suitability of text for different analyses."""
    text_stats = characteristics.get("text_statistics", {})
    text_count = text_stats.get("count", 0)
    avg_words = text_stats.get("average_words", 0)
    
    suitability = {
        "sentiment_analysis": "high" if text_count >= 10 and avg_words >= 10 else "medium" if text_count >= 5 else "low",
        "thematic_analysis": "high" if text_count >= 20 and avg_words >= 15 else "medium" if text_count >= 10 else "low",
        "content_analysis": "high" if text_count >= 5 else "medium" if text_count >= 3 else "low",
        "coding": "high" if text_count >= 15 and avg_words >= 20 else "medium" if text_count >= 8 else "low"
    }
    
    return suitability

def _get_preprocessing_recommendations(characteristics: Dict[str, Any]) -> List[str]:
    """Get text preprocessing recommendations."""
    recommendations = []
    
    text_stats = characteristics.get("text_statistics", {})
    avg_words = text_stats.get("average_words", 0)
    lexical_diversity = text_stats.get("lexical_diversity", 0)
    
    if avg_words < 5:
        recommendations.append("Texts are very short - consider combining related texts")
    
    if lexical_diversity < 0.3:
        recommendations.append("Low lexical diversity - check for repetitive content")
    
    if avg_words > 200:
        recommendations.append("Very long texts - consider splitting into segments")
    
    recommendations.extend([
        "Remove or standardize special characters",
        "Consider stemming or lemmatization for thematic analysis",
        "Check for and handle duplicate or near-duplicate texts"
    ])
    
    return recommendations

def _get_type_based_recommendations(type_detection: Dict[str, Any]) -> List[str]:
    """Get recommendations based on detected data type."""
    data_type = type_detection["primary_data_type"]
    confidence = type_detection["confidence"]
    
    recommendations = []
    
    if confidence < 0.5:
        recommendations.append("Data type detection has low confidence - manual review recommended")
    
    type_recommendations = {
        "interview": [
            "Use thematic analysis to identify key themes",
            "Consider coding for systematic analysis",
            "Sentiment analysis may reveal participant attitudes"
        ],
        "survey": [
            "Use content analysis for open-ended responses",
            "Compare responses across demographic groups",
            "Quantify response patterns and frequencies"
        ],
        "open_ended": [
            "Thematic analysis is highly recommended",
            "Consider sentiment analysis for opinion data",
            "Use coding to categorize responses systematically"
        ],
        "structured": [
            "Content analysis will work well",
            "Consider quantitative coding approaches",
            "Look for patterns in structure and format"
        ],
        "narrative": [
            "Narrative analysis techniques recommended",
            "Thematic analysis for story elements",
            "Consider chronological or causal analysis"
        ]
    }
    
    recommendations.extend(type_recommendations.get(data_type, [
        "Use content analysis as a starting point",
        "Consider multiple analysis approaches"
    ]))
    
    return recommendations

def _explain_qualitative_parameters(method_name: str, config: Dict[str, Any]) -> Dict[str, str]:
    """Explain parameters for qualitative methods."""
    explanations = {
        "sentiment_analysis": {
            "batch_size": "Number of texts to process at once",
            "include_emotions": "Whether to analyze emotional content beyond sentiment",
            "confidence_threshold": "Minimum confidence level for sentiment classification",
            "category_detail": "Level of detail in sentiment categories"
        },
        "thematic_analysis": {
            "n_themes": "Number of themes to identify",
            "method": "Algorithm used for theme identification",
            "min_theme_size": "Minimum number of texts per theme",
            "keywords_per_theme": "Number of keywords to extract per theme"
        },
        "content_analysis": {
            "analyze_structure": "Whether to analyze text structure patterns",
            "analyze_patterns": "Whether to identify recurring patterns",
            "include_linguistic_features": "Whether to include linguistic analysis",
            "custom_categories": "Pre-defined categories for analysis"
        },
        "coding": {
            "auto_code_keywords": "Whether to automatically suggest codes",
            "hierarchical_coding": "Whether to use hierarchical code structure",
            "inter_coder_reliability": "Whether to calculate reliability metrics",
            "code_complexity": "Level of coding detail (simple/detailed)"
        }
    }
    
    method_explanations = explanations.get(method_name, {})
    return {param: method_explanations.get(param, f"Parameter for {method_name}") 
            for param in config.keys() if param not in ["analysis_type", "data_type", "confidence"]}

def _get_qualitative_execution_guidance(method_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Get execution guidance for qualitative methods."""
    base_guidance = {
        "recommended_order": 1,
        "prerequisites": ["text_preprocessing"],
        "expected_output": "Qualitative insights and patterns",
        "interpretation_notes": "Focus on meaning and context"
    }
    
    method_specific = {
        "sentiment_analysis": {
            "recommended_order": 1,
            "prerequisites": ["text_cleaning"],
            "expected_output": "Sentiment scores, emotional indicators",
            "interpretation_notes": "Consider context and domain-specific sentiment"
        },
        "thematic_analysis": {
            "recommended_order": 2,
            "prerequisites": ["text_preprocessing", "initial_reading"],
            "expected_output": "Themes, sub-themes, supporting quotes",
            "interpretation_notes": "Themes should be distinct and meaningful"
        },
        "content_analysis": {
            "recommended_order": 1,
            "prerequisites": ["category_definition"],
            "expected_output": "Category frequencies, pattern analysis",
            "interpretation_notes": "Ensure categories are mutually exclusive"
        },
        "coding": {
            "recommended_order": 3,
            "prerequisites": ["initial_analysis", "code_development"],
            "expected_output": "Coded segments, code frequencies, patterns",
            "interpretation_notes": "Maintain consistency in code application"
        }
    }
    
    base_guidance.update(method_specific.get(method_name, {}))
    return base_guidance

def _get_text_requirements(method_name: str) -> Dict[str, Any]:
    """Get text requirements for specific methods."""
    requirements = {
        "sentiment_analysis": {
            "min_texts": 5,
            "min_words_per_text": 5,
            "content_type": "Opinion or emotional content",
            "preprocessing": "Remove noise, standardize format"
        },
        "thematic_analysis": {
            "min_texts": 10,
            "min_words_per_text": 15,
            "content_type": "Rich, descriptive content",
            "preprocessing": "Clean text, remove duplicates"
        },
        "content_analysis": {
            "min_texts": 5,
            "min_words_per_text": 10,
            "content_type": "Any structured text",
            "preprocessing": "Standardize format, define categories"
        },
        "coding": {
            "min_texts": 8,
            "min_words_per_text": 20,
            "content_type": "Complex, detailed responses",
            "preprocessing": "Thorough cleaning, segmentation"
        }
    }
    
    return requirements.get(method_name, {
        "min_texts": 5,
        "min_words_per_text": 10,
        "content_type": "Any text content",
        "preprocessing": "Basic text cleaning"
    })

def _get_recommendation_rationale(texts: List[str], recommendation: str, focus: str) -> str:
    """Get rationale for method recommendation."""
    text_count = len(texts)
    avg_words = sum(len(text.split()) for text in texts) / len(texts) if texts else 0
    
    rationales = {
        "sentiment_analysis": f"Detected {text_count} texts with average {avg_words:.1f} words - suitable for sentiment analysis",
        "thematic_analysis": f"Text corpus of {text_count} texts provides good basis for theme identification",
        "content_analysis": f"Structured approach suitable for {text_count} texts with varied content",
        "coding": f"Detailed coding approach appropriate for {text_count} complex texts"
    }
    
    base_rationale = rationales.get(recommendation, f"Method recommended based on {text_count} texts")
    
    if focus != "auto":
        base_rationale += f" (focused on {focus} analysis)"
    
    return base_rationale

def _estimate_qualitative_analysis_time(method: str, text_count: int) -> str:
    """Estimate analysis time for qualitative methods."""
    base_times = {
        "sentiment_analysis": 2,
        "thematic_analysis": 15,
        "content_analysis": 10,
        "coding": 25
    }
    
    base_time = base_times.get(method, 10)
    
    # Adjust for text count
    if text_count > 100:
        base_time *= 2
    elif text_count > 50:
        base_time *= 1.5
    
    if base_time < 5:
        return "< 5 minutes"
    elif base_time < 15:
        return "< 15 minutes"
    elif base_time < 60:
        return "< 1 hour"
    else:
        return "1-3 hours"

def _get_qualitative_next_steps(method: str) -> List[str]:
    """Get next steps for qualitative analysis."""
    base_steps = [
        "Prepare and clean text data",
        "Review method parameters",
        "Execute the analysis",
        "Interpret results in context"
    ]
    
    method_steps = {
        "sentiment_analysis": [
            "Prepare text data for sentiment analysis",
            "Choose appropriate sentiment lexicon",
            "Run sentiment analysis",
            "Validate results with manual review"
        ],
        "thematic_analysis": [
            "Read through texts for familiarization",
            "Develop initial coding framework",
            "Identify and refine themes",
            "Validate themes with additional review"
        ],
        "content_analysis": [
            "Define analysis categories",
            "Create coding scheme",
            "Apply codes systematically",
            "Analyze patterns and frequencies"
        ]
    }
    
    return method_steps.get(method, base_steps)

def _get_text_summary(texts: List[str]) -> Dict[str, Any]:
    """Get summary information about texts."""
    if not texts:
        return {"error": "No texts provided"}
    
    word_counts = [len(text.split()) for text in texts]
    
    return {
        "count": len(texts),
        "total_words": sum(word_counts),
        "average_words": sum(word_counts) / len(word_counts),
        "shortest_text": min(word_counts),
        "longest_text": max(word_counts),
        "sample_text": texts[0][:100] + "..." if len(texts[0]) > 100 else texts[0]
    }

def _categorize_qualitative_methods(methods: Dict[str, Any]) -> Dict[str, List[str]]:
    """Categorize qualitative methods by approach."""
    return {
        "exploratory": ["thematic_analysis", "content_analysis"],
        "confirmatory": ["coding", "survey_analysis"],
        "sentiment_emotion": ["sentiment_analysis"],
        "specialized": ["survey_analysis"]
    }

def _get_text_type_guide() -> Dict[str, Dict[str, str]]:
    """Get guide for different text types."""
    return {
        "interview": {
            "description": "Transcripts from interviews or conversations",
            "characteristics": "Question-answer format, conversational language",
            "best_methods": "thematic_analysis, coding",
            "considerations": "Consider interviewer vs respondent text separately"
        },
        "survey": {
            "description": "Open-ended survey responses",
            "characteristics": "Short to medium responses, focused topics",
            "best_methods": "content_analysis, sentiment_analysis",
            "considerations": "May have structured response patterns"
        },
        "narrative": {
            "description": "Stories, experiences, or sequential accounts",
            "characteristics": "Temporal structure, story elements",
            "best_methods": "thematic_analysis, narrative_analysis",
            "considerations": "Pay attention to sequence and causation"
        },
        "opinion": {
            "description": "Reviews, comments, opinion pieces",
            "characteristics": "Evaluative language, personal perspectives",
            "best_methods": "sentiment_analysis, thematic_analysis",
            "considerations": "Context and domain matter for sentiment"
        }
    }

def _get_qualitative_usage_guidelines() -> Dict[str, str]:
    """Get usage guidelines for qualitative methods."""
    return {
        "sentiment_analysis": "Best for opinion data, reviews, social media content",
        "thematic_analysis": "Ideal for interview data, open-ended responses, rich narratives",
        "content_analysis": "Suitable for any text where categories can be defined",
        "coding": "Best for complex, detailed texts requiring systematic analysis",
        "survey_analysis": "Specialized for survey response data with structured questions"
    }

def _generate_text_report(results: Dict[str, Any], texts: List[str]) -> str:
    """Generate comprehensive text analysis report."""
    report = "Qualitative Analysis Auto-Detection Report\n"
    report += "=" * 50 + "\n\n"
    
    # Data overview
    data_detection = results["data_detection"]
    report += "Text Data Overview:\n"
    report += f"- Number of texts: {len(texts)}\n"
    report += f"- Primary data type: {data_detection['primary_data_type']}\n"
    report += f"- Detection confidence: {data_detection['confidence']:.2f}\n"
    report += f"- Average words per text: {data_detection['data_characteristics']['avg_words_per_text']:.1f}\n"
    report += f"- Lexical diversity: {data_detection['data_characteristics']['lexical_diversity']:.3f}\n\n"
    
    # Method recommendations
    method_suggestions = results["method_suggestions"]
    if method_suggestions["primary_recommendations"]:
        report += "Recommended Analysis Methods:\n"
        report += "-" * 35 + "\n"
        
        for i, rec in enumerate(method_suggestions["primary_recommendations"][:3], 1):
            method_name = rec['method'] if isinstance(rec, dict) else rec.method
            score = rec['score'] if isinstance(rec, dict) else rec.score
            rationale = rec['rationale'] if isinstance(rec, dict) else rec.rationale
            
            report += f"{i}. {method_name.replace('_', ' ').title()}\n"
            report += f"   Confidence: {score:.2f}\n"
            report += f"   Rationale: {rationale}\n\n"
    
    # Analysis workflow
    workflow = results["recommended_workflow"]
    if workflow and "primary_method" in workflow:
        report += "Recommended Analysis Workflow:\n"
        report += "-" * 35 + "\n"
        report += f"1. Primary method: {workflow['primary_method']}\n"
        if workflow.get("secondary_methods"):
            report += f"2. Secondary methods: {', '.join(workflow['secondary_methods'])}\n"
        report += "\n"
    
    # Analysis summary
    summary = results["analysis_summary"]
    report += "Analysis Readiness Assessment:\n"
    report += "-" * 35 + "\n"
    report += f"- Best method: {summary.get('best_method', 'Not determined')}\n"
    report += f"- Readiness score: {summary.get('readiness_score', 0):.2f}\n"
    
    return report

def _get_representative_examples(texts: List[str], n_examples: int = 3) -> List[Dict[str, str]]:
    """Get representative text examples."""
    if not texts:
        return []
    
    # Sort by length to get varied examples
    sorted_texts = sorted(texts, key=len)
    
    examples = []
    if len(texts) >= 3:
        # Get short, medium, and long examples
        indices = [0, len(sorted_texts) // 2, -1]
        labels = ["Short example", "Medium example", "Long example"]
        
        for i, (idx, label) in enumerate(zip(indices, labels)):
            if i < n_examples:
                text = sorted_texts[idx]
                examples.append({
                    "label": label,
                    "text": text[:200] + "..." if len(text) > 200 else text,
                    "word_count": len(text.split())
                })
    else:
        # Just return what we have
        for i, text in enumerate(texts[:n_examples]):
            examples.append({
                "label": f"Example {i+1}",
                "text": text[:200] + "..." if len(text) > 200 else text,
                "word_count": len(text.split())
            })
    
    return examples 