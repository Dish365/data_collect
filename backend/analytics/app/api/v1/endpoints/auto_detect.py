"""
Auto-detection endpoints for data analysis.
Provides comprehensive analysis using the unified auto-detection system.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import pandas as pd
import json

from core.database import get_db
from app.analytics.auto_detect import (
    UnifiedAutoDetector,
    create_auto_detector,
    get_analysis_for_api,
    analyze_comprehensive_data
)

router = APIRouter()

@router.post("/analyze/comprehensive")
async def analyze_comprehensive(
    data: Dict[str, Any],
    analysis_type: str = "auto",
    include_descriptive: bool = True,
    include_inferential: bool = True,
    include_qualitative: bool = True,
    target_variable: Optional[str] = None,
    grouping_variable: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform comprehensive analysis using all available modules.
    
    Args:
        data: Input data as a dictionary
        analysis_type: Type of analysis ("auto", "basic", "comprehensive")
        include_descriptive: Whether to include descriptive analytics
        include_inferential: Whether to include inferential analytics  
        include_qualitative: Whether to include qualitative analytics
        target_variable: Target/dependent variable for analysis
        grouping_variable: Grouping/independent variable
        db: Database session
        
    Returns:
        Comprehensive analysis results with cross-module insights
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Use the unified auto-detection system
        results = analyze_comprehensive_data(
            df,
            analysis_type=analysis_type,
            include_descriptive=include_descriptive,
            include_inferential=include_inferential,
            include_qualitative=include_qualitative,
            target_variable=target_variable,
            grouping_variable=grouping_variable
        )
        
        # Convert to API-friendly format
        return _format_comprehensive_results(results)
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error in comprehensive analysis: {str(e)}"
        )

@router.post("/analyze/descriptive")
async def analyze_descriptive(
    data: Dict[str, Any],
    analysis_goals: Optional[List[str]] = None,
    target_variables: Optional[List[str]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform descriptive analysis only.
    
    Args:
        data: Input data as a dictionary
        analysis_goals: Optional list of analysis goals
        target_variables: Optional list of target variables
        db: Database session
        
    Returns:
        Descriptive analysis results and recommendations
    """
    try:
        df = pd.DataFrame(data)
        detector = create_auto_detector("descriptive")
        
        suggestions = detector.suggest_analyses(df, analysis_goals=analysis_goals)
        characteristics = detector.detect_data_characteristics(df)
        
        return {
            "module": "descriptive",
            "data_overview": _format_data_overview(characteristics),
            "recommendations": _format_suggestions(suggestions),
            "suggested_workflow": _get_descriptive_workflow(suggestions),
            "quality_assessment": _assess_data_quality(characteristics)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error in descriptive analysis: {str(e)}"
        )

@router.post("/analyze/inferential")
async def analyze_inferential(
    data: Dict[str, Any],
    target_variable: Optional[str] = None,
    grouping_variable: Optional[str] = None,
    research_question: Optional[str] = None,
    alpha: float = 0.05,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform inferential statistical analysis.
    
    Args:
        data: Input data as a dictionary
        target_variable: Dependent variable name
        grouping_variable: Independent/grouping variable name
        research_question: Type of research question
        alpha: Significance level
        db: Database session
        
    Returns:
        Inferential analysis results and test recommendations
    """
    try:
        df = pd.DataFrame(data)
        detector = create_auto_detector("inferential")
        
        suggestions = detector.suggest_analyses(
            df, 
            target_variable=target_variable,
            grouping_variable=grouping_variable,
            research_question=research_question,
            alpha=alpha
        )
        characteristics = detector.detect_data_characteristics(df)
        
        return {
            "module": "inferential",
            "data_overview": _format_data_overview(characteristics),
            "test_recommendations": _format_suggestions(suggestions),
            "research_design": _infer_research_design(characteristics, target_variable, grouping_variable),
            "power_considerations": _assess_statistical_power(characteristics, suggestions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error in inferential analysis: {str(e)}"
        )

@router.post("/analyze/qualitative")
async def analyze_qualitative(
    data: Dict[str, Any],
    text_columns: Optional[List[str]] = None,
    research_goals: Optional[List[str]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform qualitative text analysis.
    
    Args:
        data: Input data as a dictionary
        text_columns: Specific text columns to analyze
        research_goals: Optional research objectives
        db: Database session
        
    Returns:
        Qualitative analysis results and method recommendations
    """
    try:
        df = pd.DataFrame(data)
        detector = create_auto_detector("qualitative")
        
        # Extract text data if specific columns provided
        kwargs = {}
        if text_columns:
            texts = []
            for col in text_columns:
                if col in df.columns:
                    texts.extend(df[col].dropna().astype(str).tolist())
            kwargs['texts'] = texts
        
        suggestions = detector.suggest_analyses(df, analysis_goals=research_goals, **kwargs)
        characteristics = detector.detect_data_characteristics(df, **kwargs)
        
        return {
            "module": "qualitative",
            "data_overview": _format_data_overview(characteristics),
            "method_recommendations": _format_suggestions(suggestions),
            "text_characteristics": _get_text_characteristics(df, text_columns),
            "analysis_readiness": _assess_qualitative_readiness(characteristics, suggestions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error in qualitative analysis: {str(e)}"
        )

@router.post("/data-characteristics")
async def get_data_characteristics(
    data: Dict[str, Any],
    variable_metadata: Optional[List[Dict[str, Any]]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive data characteristics and profiling.
    
    Args:
        data: Input data as a dictionary
        variable_metadata: Optional metadata about variables
        db: Database session
        
    Returns:
        Detailed data characteristics and quality assessment
    """
    try:
        df = pd.DataFrame(data)
        unified_detector = UnifiedAutoDetector()
        
        characteristics = unified_detector.data_profiler.profile_data(df)
        
        return {
            "data_profile": _format_data_characteristics(characteristics),
            "quality_report": _generate_quality_report(characteristics),
            "variable_analysis": _analyze_variables(characteristics),
            "recommendations": _get_data_improvement_recommendations(characteristics)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error analyzing data characteristics: {str(e)}"
        )

@router.post("/suggest-methods")
async def suggest_analysis_methods(
    data: Dict[str, Any],
    analysis_focus: Optional[str] = "auto",
    research_context: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get intelligent analysis method suggestions across all modules.
    
    Args:
        data: Input data as a dictionary
        analysis_focus: Focus area ("auto", "descriptive", "inferential", "qualitative")
        research_context: Optional research context information
        db: Database session
        
    Returns:
        Intelligent method suggestions with rationale
    """
    try:
        df = pd.DataFrame(data)
        
        # Use the API helper for standardized response
        api_response = get_analysis_for_api(df, analysis_type=analysis_focus)
        
        # Enhance with method-specific details
        enhanced_response = api_response.copy()
        enhanced_response["method_details"] = _get_method_details(api_response)
        enhanced_response["integration_opportunities"] = _find_integration_opportunities(api_response)
        enhanced_response["next_steps"] = _suggest_next_steps(api_response)
        
        return enhanced_response
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error suggesting methods: {str(e)}"
        )

@router.post("/configure/{method_name}")
async def configure_analysis_method(
    method_name: str,
    data: Dict[str, Any],
    target_variable: Optional[str] = None,
    grouping_variable: Optional[str] = None,
    custom_parameters: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Auto-configure parameters for a specific analysis method.
    
    Args:
        method_name: Name of the analysis method to configure
        data: Input data as a dictionary
        target_variable: Target variable (if applicable)
        grouping_variable: Grouping variable (if applicable)
        custom_parameters: Optional custom parameter overrides
        db: Database session
        
    Returns:
        Optimized configuration for the specified method
    """
    try:
        df = pd.DataFrame(data)
        
        # Determine which detector to use based on method name
        detector_type = _determine_detector_type(method_name)
        detector = create_auto_detector(detector_type)
        
        # Get auto-configuration
        if detector_type == "descriptive":
            config = detector.auto_configure_analysis(method_name, df)
        elif detector_type == "inferential":
            config = detector.auto_configure_test(method_name, df, target_variable, grouping_variable)
        elif detector_type == "qualitative":
            # Extract texts for qualitative analysis
            texts = _extract_texts_from_data(df)
            config = detector.auto_configure_analysis(texts, method_name)
        else:
            raise ValueError(f"Unknown detector type for method: {method_name}")
        
        # Apply custom parameter overrides
        if custom_parameters:
            config.update(custom_parameters)
        
        return {
            "method": method_name,
            "detector_type": detector_type,
            "configuration": config,
            "parameter_explanation": _explain_parameters(method_name, config),
            "execution_guidance": _get_execution_guidance(method_name, config)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error configuring method {method_name}: {str(e)}"
        )

@router.get("/methods")
async def list_available_methods(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    List all available analysis methods across modules.
    
    Returns:
        Dictionary of available methods by category
    """
    try:
        # Get method requirements from each detector
        descriptive_detector = create_auto_detector("descriptive")
        inferential_detector = create_auto_detector("inferential")
        qualitative_detector = create_auto_detector("qualitative")
        
        return {
            "descriptive_methods": descriptive_detector.get_method_requirements(),
            "inferential_methods": inferential_detector.get_method_requirements(),
            "qualitative_methods": qualitative_detector.get_method_requirements(),
            "unified_workflows": _get_unified_workflows(),
            "integration_patterns": _get_integration_patterns()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing methods: {str(e)}"
        )


# Helper functions for formatting and processing responses

def _format_comprehensive_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """Format comprehensive analysis results for API response."""
    formatted = {
        "status": "success",
        "analysis_type": "comprehensive",
        "data_overview": _format_data_overview(results["data_characteristics"]),
        "modules_used": results["coordination"]["modules_used"],
        "module_results": {},
        "cross_module_insights": results["coordination"]["cross_module_insights"],
        "unified_recommendations": results["coordination"]["unified_recommendations"],
        "execution_summary": {
            "timestamp": results["data_characteristics"].detection_timestamp,
            "processing_notes": []
        }
    }
    
    # Format each module's results
    for module_name, module_result in results["module_results"].items():
        if "error" not in module_result:
            formatted["module_results"][module_name] = {
                "available": True,
                "recommendations": _format_suggestions(module_result["suggestions"]),
                "confidence_scores": _extract_confidence_scores(module_result["suggestions"])
            }
        else:
            formatted["module_results"][module_name] = {
                "available": False,
                "error": module_result["error"]
            }
    
    return formatted

def _format_data_overview(characteristics) -> Dict[str, Any]:
    """Format data characteristics for API response."""
    return {
        "sample_size": characteristics.n_observations,
        "variables": characteristics.n_variables,
        "data_shape": characteristics.data_shape,
        "data_types": {str(k.value): v for k, v in characteristics.type_counts.items()},
        "quality_score": characteristics.completeness_score,
        "missing_data_percentage": characteristics.missing_percentage,
        "sample_size_category": characteristics.sample_size_category,
        "has_text": getattr(characteristics, 'has_text', False),
        "has_datetime": getattr(characteristics, 'has_datetime', False),
        "has_geographic": getattr(characteristics, 'has_geographic', False)
    }

def _format_suggestions(suggestions) -> List[Dict[str, Any]]:
    """Format analysis suggestions for API response."""
    formatted = []
    
    if hasattr(suggestions, 'primary_recommendations'):
        for rec in suggestions.primary_recommendations:
            formatted.append({
                "method": rec.method,
                "score": rec.score,
                "confidence": rec.confidence.value,
                "rationale": rec.rationale,
                "estimated_time": rec.estimated_time,
                "function_call": rec.function_call,
                "parameters": rec.parameters,
                "category": "primary"
            })
        
        for rec in suggestions.secondary_recommendations:
            formatted.append({
                "method": rec.method,
                "score": rec.score,
                "confidence": rec.confidence.value,
                "rationale": rec.rationale,
                "estimated_time": rec.estimated_time,
                "function_call": rec.function_call,
                "parameters": rec.parameters,
                "category": "secondary"
            })
    
    return formatted

def _extract_confidence_scores(suggestions) -> Dict[str, float]:
    """Extract confidence scores from suggestions."""
    scores = {}
    
    if hasattr(suggestions, 'primary_recommendations'):
        for rec in suggestions.primary_recommendations:
            scores[rec.method] = rec.score
        for rec in suggestions.secondary_recommendations:
            scores[rec.method] = rec.score
    
    return scores

def _get_descriptive_workflow(suggestions) -> Dict[str, Any]:
    """Generate descriptive analysis workflow."""
    workflow = {
        "suggested_order": [],
        "parallel_analyses": [],
        "dependencies": {},
        "estimated_total_time": "< 10 minutes"
    }
    
    if hasattr(suggestions, 'analysis_order'):
        workflow["suggested_order"] = suggestions.analysis_order
    
    return workflow

def _assess_data_quality(characteristics) -> Dict[str, Any]:
    """Assess data quality for descriptive analysis."""
    quality = {
        "overall_grade": "A",
        "completeness": characteristics.completeness_score,
        "readiness_score": min(1.0, characteristics.completeness_score / 100),
        "issues": [],
        "recommendations": []
    }
    
    if characteristics.missing_percentage > 20:
        quality["issues"].append("High missing data percentage")
        quality["overall_grade"] = "C"
    
    if characteristics.n_observations < 30:
        quality["issues"].append("Small sample size")
        quality["recommendations"].append("Consider collecting more data")
    
    return quality

def _infer_research_design(characteristics, target_variable: str, grouping_variable: str) -> Dict[str, Any]:
    """Infer research design from data characteristics."""
    design = {
        "type": "exploratory",
        "comparison_type": "descriptive",
        "variables": {
            "target": target_variable,
            "grouping": grouping_variable
        }
    }
    
    if target_variable and grouping_variable:
        design["type"] = "comparative"
        design["comparison_type"] = "between_groups"
    elif len(characteristics.variable_types) >= 2:
        design["type"] = "correlational"
        design["comparison_type"] = "association"
    
    return design

def _assess_statistical_power(characteristics, suggestions) -> Dict[str, Any]:
    """Assess statistical power considerations."""
    power_assessment = {
        "sample_size_adequacy": characteristics.sample_size_category,
        "power_concerns": [],
        "recommendations": []
    }
    
    if characteristics.n_observations < 30:
        power_assessment["power_concerns"].append("Small sample size may affect test power")
        power_assessment["recommendations"].append("Consider non-parametric alternatives")
    
    if characteristics.missing_percentage > 20:
        power_assessment["power_concerns"].append("High missing data may reduce effective sample size")
        power_assessment["recommendations"].append("Address missing data before analysis")
    
    return power_assessment

def _get_text_characteristics(df: pd.DataFrame, text_columns: Optional[List[str]]) -> Dict[str, Any]:
    """Get characteristics specific to text data."""
    text_chars = {
        "text_columns_found": [],
        "total_texts": 0,
        "average_text_length": 0,
        "text_quality": "unknown"
    }
    
    # Find text columns if not specified
    if text_columns is None:
        text_columns = df.select_dtypes(include=['object']).columns.tolist()
    
    for col in text_columns:
        if col in df.columns:
            col_texts = df[col].dropna().astype(str)
            if len(col_texts) > 0 and col_texts.str.len().mean() > 10:
                text_chars["text_columns_found"].append(col)
                text_chars["total_texts"] += len(col_texts)
                text_chars["average_text_length"] += col_texts.str.len().mean()
    
    if text_chars["text_columns_found"]:
        text_chars["average_text_length"] /= len(text_chars["text_columns_found"])
        text_chars["text_quality"] = "good" if text_chars["average_text_length"] > 20 else "limited"
    
    return text_chars

def _assess_qualitative_readiness(characteristics, suggestions) -> Dict[str, Any]:
    """Assess readiness for qualitative analysis."""
    readiness = {
        "overall_score": 0.5,
        "readiness_factors": {},
        "recommendations": []
    }
    
    if hasattr(suggestions, 'primary_recommendations') and suggestions.primary_recommendations:
        readiness["overall_score"] = min(1.0, len(suggestions.primary_recommendations) / 3)
        readiness["readiness_factors"]["method_availability"] = len(suggestions.primary_recommendations)
    
    if hasattr(characteristics, 'has_text') and characteristics.has_text:
        readiness["readiness_factors"]["text_data_present"] = True
    else:
        readiness["recommendations"].append("Ensure adequate text data is available")
    
    return readiness

def _format_data_characteristics(characteristics) -> Dict[str, Any]:
    """Format data characteristics for detailed profiling."""
    return {
        "basic_info": _format_data_overview(characteristics),
        "variable_details": {
            var: {"type": str(dtype.value), "summary": "Available"} 
            for var, dtype in characteristics.variable_types.items()
        },
        "data_quality": {
            "completeness": characteristics.completeness_score,
            "missing_data": characteristics.missing_percentage,
            "duplicate_rows": getattr(characteristics, 'duplicate_rows', 0),
            "constant_columns": getattr(characteristics, 'constant_columns', [])
        },
        "statistical_summary": getattr(characteristics, 'numeric_summaries', {})
    }

def _generate_quality_report(characteristics) -> Dict[str, Any]:
    """Generate comprehensive data quality report."""
    quality = {
        "overall_grade": "A",
        "issues_found": [],
        "strengths": [],
        "improvement_suggestions": []
    }
    
    if characteristics.completeness_score >= 95:
        quality["strengths"].append("Excellent data completeness")
    elif characteristics.completeness_score < 80:
        quality["issues_found"].append("Significant missing data")
        quality["overall_grade"] = "C"
    
    if characteristics.n_observations >= 100:
        quality["strengths"].append("Adequate sample size")
    elif characteristics.n_observations < 30:
        quality["issues_found"].append("Small sample size")
    
    return quality

def _analyze_variables(characteristics) -> Dict[str, Any]:
    """Analyze individual variables."""
    from ..auto_detect.base_detector import DataType
    
    analysis = {
        "variable_count_by_type": {str(k.value): v for k, v in characteristics.type_counts.items()},
        "recommended_transformations": {},
        "variable_relationships": "Not analyzed"
    }
    
    # Add transformation recommendations
    for var, dtype in characteristics.variable_types.items():
        if dtype == DataType.CATEGORICAL and var in getattr(characteristics, 'high_cardinality_vars', []):
            analysis["recommended_transformations"][var] = "Consider grouping categories"
    
    return analysis

def _get_data_improvement_recommendations(characteristics) -> List[str]:
    """Get recommendations for data improvement."""
    recommendations = []
    
    if characteristics.missing_percentage > 10:
        recommendations.append("Address missing data through imputation or collection")
    
    if characteristics.n_observations < 50:
        recommendations.append("Consider collecting more data for robust analysis")
    
    if hasattr(characteristics, 'constant_columns') and characteristics.constant_columns:
        recommendations.append("Remove constant columns that provide no information")
    
    return recommendations

def _get_method_details(api_response: Dict[str, Any]) -> Dict[str, Any]:
    """Get detailed information about suggested methods."""
    details = {
        "method_categories": {},
        "complexity_levels": {},
        "time_estimates": {}
    }
    
    # Categorize methods by module
    for analysis_type in ["descriptive", "inferential", "qualitative"]:
        analysis_key = f"{analysis_type}_analysis"
        if analysis_key in api_response and api_response[analysis_key].get("available"):
            recommendations = api_response[analysis_key].get("recommendations", [])
            details["method_categories"][analysis_type] = [r.get("method") for r in recommendations]
    
    return details

def _find_integration_opportunities(api_response: Dict[str, Any]) -> List[str]:
    """Find opportunities for integrating multiple analysis approaches."""
    opportunities = []
    
    available_modules = []
    for analysis_type in ["descriptive", "inferential", "qualitative"]:
        analysis_key = f"{analysis_type}_analysis"
        if analysis_key in api_response and api_response[analysis_key].get("available"):
            available_modules.append(analysis_type)
    
    if len(available_modules) >= 2:
        opportunities.append("Cross-validate findings across multiple analytical approaches")
    
    if "descriptive" in available_modules and "inferential" in available_modules:
        opportunities.append("Use descriptive insights to inform statistical test selection")
    
    if "qualitative" in available_modules:
        opportunities.append("Triangulate quantitative findings with qualitative insights")
    
    return opportunities

def _suggest_next_steps(api_response: Dict[str, Any]) -> List[str]:
    """Suggest next steps based on analysis results."""
    next_steps = []
    
    if api_response.get("status") == "success":
        next_steps.append("Review recommended methods and select based on research goals")
        next_steps.append("Configure selected methods using the /configure endpoint")
        next_steps.append("Execute analyses in the suggested order")
    
    return next_steps

def _determine_detector_type(method_name: str) -> str:
    """Determine which detector type to use for a given method."""
    descriptive_methods = {
        "basic_statistics", "distribution_analysis", "correlation_analysis",
        "categorical_analysis", "cross_tabulation", "outlier_detection",
        "missing_data_analysis", "temporal_analysis", "geospatial_analysis",
        "grouped_analysis"
    }
    
    inferential_methods = {
        "one_sample_t_test", "two_sample_t_test", "paired_t_test", "welch_t_test",
        "mann_whitney_u", "wilcoxon_signed_rank", "one_way_anova", "kruskal_wallis",
        "chi_square_independence", "chi_square_goodness_of_fit", "fisher_exact",
        "correlation_test", "linear_regression", "logistic_regression", "bootstrap_test"
    }
    
    qualitative_methods = {
        "sentiment_analysis", "thematic_analysis", "content_analysis",
        "coding", "survey_analysis"
    }
    
    if method_name in descriptive_methods:
        return "descriptive"
    elif method_name in inferential_methods:
        return "inferential"
    elif method_name in qualitative_methods:
        return "qualitative"
    else:
        raise ValueError(f"Unknown method: {method_name}")

def _extract_texts_from_data(df: pd.DataFrame) -> List[str]:
    """Extract text data from DataFrame for qualitative analysis."""
    texts = []
    text_cols = df.select_dtypes(include=['object']).columns
    
    for col in text_cols:
        if hasattr(df[col], 'str') and df[col].str.len().mean() > 20:
            texts.extend(df[col].dropna().astype(str).tolist())
    
    return texts

def _explain_parameters(method_name: str, config: Dict[str, Any]) -> Dict[str, str]:
    """Provide explanations for configuration parameters."""
    explanations = {}
    
    for param, value in config.items():
        if param == "alpha":
            explanations[param] = f"Significance level for hypothesis testing (Type I error rate)"
        elif param == "confidence_level":
            explanations[param] = f"Confidence level for interval estimation"
        elif param == "n_themes":
            explanations[param] = f"Number of themes to extract in thematic analysis"
        elif param == "batch_size":
            explanations[param] = f"Number of texts to process in each batch"
        else:
            explanations[param] = f"Configuration parameter for {method_name}"
    
    return explanations

def _get_execution_guidance(method_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Provide guidance for executing the configured method."""
    guidance = {
        "preparation_steps": [],
        "execution_notes": [],
        "interpretation_tips": []
    }
    
    if method_name in ["two_sample_t_test", "welch_t_test"]:
        guidance["preparation_steps"].append("Verify group assignments are correct")
        guidance["execution_notes"].append("Check normality assumptions before interpretation")
        guidance["interpretation_tips"].append("Consider effect size along with p-value")
    
    elif method_name in ["thematic_analysis", "content_analysis"]:
        guidance["preparation_steps"].append("Review text data for quality and consistency")
        guidance["execution_notes"].append("Consider multiple coding approaches")
        guidance["interpretation_tips"].append("Validate themes with independent reviewers")
    
    return guidance

def _get_unified_workflows() -> Dict[str, List[str]]:
    """Get predefined unified analysis workflows."""
    return {
        "exploratory_data_analysis": [
            "data_characteristics",
            "descriptive_overview",
            "correlation_analysis",
            "outlier_detection"
        ],
        "hypothesis_testing_workflow": [
            "data_characteristics",
            "assumption_checking",
            "test_selection",
            "statistical_testing",
            "effect_size_analysis"
        ],
        "mixed_methods_workflow": [
            "data_characteristics",
            "quantitative_analysis",
            "qualitative_analysis",
            "triangulation",
            "integration"
        ]
    }

def _get_integration_patterns() -> Dict[str, Dict[str, Any]]:
    """Get patterns for integrating multiple analysis types."""
    return {
        "descriptive_to_inferential": {
            "trigger": "Strong patterns found in descriptive analysis",
            "next_step": "Formulate hypotheses for statistical testing",
            "methods": ["correlation_test", "regression_analysis"]
        },
        "quantitative_to_qualitative": {
            "trigger": "Unexpected findings in quantitative analysis",
            "next_step": "Explore with qualitative methods",
            "methods": ["thematic_analysis", "content_analysis"]
        },
        "convergent_validation": {
            "trigger": "Multiple analysis types available",
            "next_step": "Cross-validate findings across methods",
            "methods": ["triangulation", "mixed_methods_integration"]
        }
    }