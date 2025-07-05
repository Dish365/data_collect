"""
Descriptive analytics endpoints with auto-detection capabilities.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import pandas as pd
import json

from core.database import get_db
from app.analytics.descriptive.auto_detection import (
    DescriptiveAutoDetector,
    auto_analyze_descriptive_data,
    quick_descriptive_recommendation
)
from app.analytics.auto_detect.base_detector import DataType

router = APIRouter()

@router.post("/analyze")
async def analyze_descriptive(
    data: Dict[str, Any],
    analysis_goals: Optional[List[str]] = None,
    target_variables: Optional[List[str]] = None,
    variable_metadata: Optional[List[Dict[str, Any]]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform comprehensive descriptive analysis with auto-detection.
    
    Args:
        data: Input data as a dictionary
        analysis_goals: Optional list of analysis goals
        target_variables: Optional list of target variables
        variable_metadata: Optional metadata about variables
        db: Database session
        
    Returns:
        Comprehensive descriptive analysis results
    """
    try:
        df = pd.DataFrame(data)
        
        # Use the auto-analysis function
        results = auto_analyze_descriptive_data(
            df,
            variable_metadata=variable_metadata,
            analysis_goals=analysis_goals
        )
        
        # Format for API response
        return {
            "status": "success",
            "analysis_type": "descriptive",
            "data_overview": _format_data_overview(results["data_characteristics"]),
            "recommendations": _format_analysis_suggestions(results["analysis_suggestions"]),
            "configuration": results["recommended_configuration"],
            "quality_assessment": _assess_data_quality(results["data_characteristics"]),
            "analysis_report": results["analysis_report"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error in descriptive analysis: {str(e)}"
        )

@router.post("/suggest-analyses")
async def suggest_descriptive_analyses(
    data: Dict[str, Any],
    analysis_goals: Optional[List[str]] = None,
    variable_metadata: Optional[List[Dict[str, Any]]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get analysis suggestions for descriptive statistics.
    
    Args:
        data: Input data as a dictionary
        analysis_goals: Optional list of analysis goals
        variable_metadata: Optional metadata about variables
        db: Database session
        
    Returns:
        Analysis suggestions and recommendations
    """
    try:
        df = pd.DataFrame(data)
        detector = DescriptiveAutoDetector()
        
        suggestions = detector.suggest_descriptive_analyses(
            df, 
            variable_metadata=variable_metadata,
            analysis_goals=analysis_goals
        )
        
        characteristics = detector.detect_data_characteristics(df, variable_metadata)
        
        return {
            "status": "success",
            "data_characteristics": _format_data_characteristics(characteristics),
            "primary_recommendations": suggestions["primary_recommendations"],
            "secondary_recommendations": suggestions["secondary_recommendations"],
            "optional_analyses": suggestions["optional_analyses"],
            "data_quality_warnings": suggestions["data_quality_warnings"],
            "analysis_order": suggestions["analysis_order"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error suggesting analyses: {str(e)}"
        )

@router.post("/configure/{method_name}")
async def configure_descriptive_method(
    method_name: str,
    data: Dict[str, Any],
    target_variables: Optional[List[str]] = None,
    custom_parameters: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Auto-configure parameters for a specific descriptive analysis method.
    
    Args:
        method_name: Name of the analysis method
        data: Input data as a dictionary
        target_variables: Optional target variables
        custom_parameters: Optional custom parameter overrides
        db: Database session
        
    Returns:
        Optimized configuration for the method
    """
    try:
        df = pd.DataFrame(data)
        detector = DescriptiveAutoDetector()
        
        config = detector.auto_configure_analysis(
            method_name, 
            df, 
            target_variables=target_variables
        )
        
        # Apply custom parameter overrides
        if custom_parameters:
            config.update(custom_parameters)
        
        return {
            "method": method_name,
            "configuration": config,
            "parameter_explanation": _explain_descriptive_parameters(method_name, config),
            "execution_guidance": _get_descriptive_execution_guidance(method_name, config)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error configuring method {method_name}: {str(e)}"
        )

@router.post("/data-characteristics")
async def get_descriptive_data_characteristics(
    data: Dict[str, Any],
    variable_metadata: Optional[List[Dict[str, Any]]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed data characteristics for descriptive analysis.
    
    Args:
        data: Input data as a dictionary
        variable_metadata: Optional metadata about variables
        db: Database session
        
    Returns:
        Detailed data characteristics and quality assessment
    """
    try:
        df = pd.DataFrame(data)
        detector = DescriptiveAutoDetector()
        
        characteristics = detector.detect_data_characteristics(df, variable_metadata)
        
        return {
            "status": "success",
            "data_profile": _format_data_characteristics(characteristics),
            "variable_analysis": _analyze_variables_descriptive(characteristics),
            "quality_report": _generate_quality_report(characteristics),
            "suitability_assessment": _assess_descriptive_suitability(characteristics),
            "recommendations": _get_data_improvement_recommendations(characteristics)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error analyzing data characteristics: {str(e)}"
        )

@router.post("/quick-recommendation")
async def get_quick_descriptive_recommendation(
    data: Dict[str, Any],
    analysis_type: str = "auto",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get quick analysis recommendation for descriptive statistics.
    
    Args:
        data: Input data as a dictionary
        analysis_type: Type of analysis ('auto', 'overview', 'quality', 'relationships')
        db: Database session
        
    Returns:
        Quick recommendation with rationale
    """
    try:
        df = pd.DataFrame(data)
        
        recommendation = quick_descriptive_recommendation(df, analysis_type)
        
        return {
            "status": "success",
            "recommendation": recommendation,
            "rationale": _get_recommendation_rationale(df, recommendation),
            "estimated_time": _estimate_analysis_time(recommendation, len(df)),
            "next_steps": _get_next_steps(recommendation)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error getting quick recommendation: {str(e)}"
        )

@router.get("/methods")
async def list_descriptive_methods(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    List all available descriptive analysis methods.
    
    Returns:
        Dictionary of available methods with requirements
    """
    try:
        detector = DescriptiveAutoDetector()
        methods = detector.get_method_requirements()
        
        return {
            "status": "success",
            "methods": methods,
            "method_categories": _categorize_descriptive_methods(methods),
            "usage_guidelines": _get_usage_guidelines()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing methods: {str(e)}"
        )

@router.post("/generate-report")
async def generate_descriptive_report(
    data: Dict[str, Any],
    variable_metadata: Optional[List[Dict[str, Any]]] = None,
    include_visualizations: bool = False,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate a comprehensive descriptive analysis report.
    
    Args:
        data: Input data as a dictionary
        variable_metadata: Optional metadata about variables
        include_visualizations: Whether to include visualization recommendations
        db: Database session
        
    Returns:
        Comprehensive analysis report
    """
    try:
        df = pd.DataFrame(data)
        detector = DescriptiveAutoDetector()
        
        report = detector.generate_analysis_report(df, variable_metadata)
        
        response = {
            "status": "success",
            "report": report,
            "metadata": {
                "generated_at": pd.Timestamp.now().isoformat(),
                "data_shape": df.shape,
                "analysis_type": "descriptive"
            }
        }
        
        if include_visualizations:
            response["visualization_recommendations"] = _get_visualization_recommendations(df)
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error generating report: {str(e)}"
        )

# Helper functions for descriptive analytics endpoints

def _format_data_overview(characteristics) -> Dict[str, Any]:
    """Format data characteristics for API response."""
    return {
        "sample_size": characteristics.n_observations,
        "variables": characteristics.n_variables,
        "data_shape": characteristics.data_shape,
        "data_types": {str(k.value): v for k, v in characteristics.type_counts.items()},
        "quality_score": characteristics.completeness_score,
        "missing_data_percentage": characteristics.missing_percentage,
        "sample_size_category": characteristics.sample_size_category
    }

def _format_analysis_suggestions(suggestions) -> Dict[str, Any]:
    """Format analysis suggestions for API response."""
    return {
        "primary_recommendations": suggestions["primary_recommendations"],
        "secondary_recommendations": suggestions["secondary_recommendations"],
        "optional_analyses": suggestions["optional_analyses"],
        "data_quality_warnings": suggestions["data_quality_warnings"],
        "analysis_order": suggestions["analysis_order"]
    }

def _format_data_characteristics(characteristics) -> Dict[str, Any]:
    """Format data characteristics for detailed response."""
    return {
        "basic_info": {
            "n_observations": characteristics.n_observations,
            "n_variables": characteristics.n_variables,
            "data_shape": characteristics.data_shape
        },
        "data_types": {str(k.value): v for k, v in characteristics.type_counts.items()},
        "quality_metrics": {
            "completeness_score": characteristics.completeness_score,
            "missing_percentage": characteristics.missing_percentage,
            "duplicate_rows": characteristics.duplicate_rows,
            "constant_columns": characteristics.constant_columns
        },
        "special_features": {
            "has_datetime": characteristics.has_datetime,
            "has_geographic": characteristics.has_geographic,
            "has_text": characteristics.has_text,
            "has_identifiers": characteristics.has_identifiers
        },
        "analysis_potential": {
            "potential_correlations": characteristics.potential_correlations,
            "potential_cross_tabs": characteristics.potential_cross_tabs,
            "grouping_variables": characteristics.grouping_variables
        }
    }

def _assess_data_quality(characteristics) -> Dict[str, Any]:
    """Assess data quality for descriptive analysis."""
    quality_score = characteristics.completeness_score
    
    if quality_score >= 95:
        grade = "A"
        description = "Excellent data quality"
    elif quality_score >= 85:
        grade = "B"
        description = "Good data quality"
    elif quality_score >= 70:
        grade = "C"
        description = "Fair data quality"
    else:
        grade = "D"
        description = "Poor data quality"
    
    return {
        "overall_grade": grade,
        "description": description,
        "completeness_score": quality_score,
        "missing_percentage": characteristics.missing_percentage,
        "issues": _identify_quality_issues(characteristics),
        "recommendations": _get_quality_recommendations(characteristics)
    }

def _identify_quality_issues(characteristics) -> List[str]:
    """Identify data quality issues."""
    issues = []
    
    if characteristics.missing_percentage > 20:
        issues.append("High missing data percentage")
    if characteristics.duplicate_rows > 0:
        issues.append("Duplicate rows detected")
    if characteristics.constant_columns:
        issues.append("Constant columns with no variation")
    if characteristics.n_observations < 30:
        issues.append("Small sample size")
    
    return issues

def _get_quality_recommendations(characteristics) -> List[str]:
    """Get recommendations for improving data quality."""
    recommendations = []
    
    if characteristics.missing_percentage > 10:
        recommendations.append("Consider data imputation or removal of high-missing variables")
    if characteristics.duplicate_rows > 0:
        recommendations.append("Remove duplicate rows before analysis")
    if characteristics.constant_columns:
        recommendations.append("Remove constant columns (provide no analytical value)")
    if characteristics.n_observations < 50:
        recommendations.append("Consider collecting more data for robust analysis")
    
    return recommendations

def _analyze_variables_descriptive(characteristics) -> Dict[str, Any]:
    """Analyze variables for descriptive statistics."""
    return {
        "numeric_variables": {
            "count": characteristics.type_counts.get(str(DataType.NUMERIC_CONTINUOUS.value), 0) + 
                    characteristics.type_counts.get(str(DataType.NUMERIC_DISCRETE.value), 0),
            "summaries": characteristics.numeric_summaries
        },
        "categorical_variables": {
            "count": characteristics.type_counts.get(str(DataType.CATEGORICAL.value), 0) + 
                    characteristics.type_counts.get(str(DataType.BINARY.value), 0),
            "summaries": characteristics.categorical_summaries
        },
        "special_variables": {
            "datetime_count": 1 if characteristics.has_datetime else 0,
            "geographic_count": 1 if characteristics.has_geographic else 0,
            "text_count": 1 if characteristics.has_text else 0
        }
    }

def _generate_quality_report(characteristics) -> Dict[str, Any]:
    """Generate comprehensive quality report."""
    return {
        "overall_assessment": _assess_data_quality(characteristics),
        "detailed_metrics": {
            "completeness": characteristics.completeness_score,
            "missing_data": characteristics.missing_percentage,
            "data_consistency": 100 - (characteristics.duplicate_rows / characteristics.n_observations * 100) if characteristics.n_observations > 0 else 100,
            "variable_quality": len(characteristics.constant_columns) / characteristics.n_variables * 100 if characteristics.n_variables > 0 else 0
        },
        "recommendations": _get_quality_recommendations(characteristics)
    }

def _assess_descriptive_suitability(characteristics) -> Dict[str, Any]:
    """Assess suitability for descriptive analysis."""
    suitability_score = min(100, characteristics.completeness_score + 
                           (50 if characteristics.n_observations >= 30 else 0))
    
    return {
        "suitability_score": suitability_score,
        "readiness_level": "High" if suitability_score >= 80 else 
                          "Medium" if suitability_score >= 60 else "Low",
        "recommended_analyses": _get_recommended_analyses_by_suitability(characteristics),
        "limitations": _identify_analysis_limitations(characteristics)
    }

def _get_recommended_analyses_by_suitability(characteristics) -> List[str]:
    """Get recommended analyses based on data suitability."""
    recommendations = ["basic_statistics"]
    
    if characteristics.n_observations >= 30:
        recommendations.append("distribution_analysis")
    if characteristics.potential_correlations > 0:
        recommendations.append("correlation_analysis")
    if characteristics.potential_cross_tabs > 0:
        recommendations.append("cross_tabulation")
    if characteristics.missing_percentage > 5:
        recommendations.append("missing_data_analysis")
    
    return recommendations

def _identify_analysis_limitations(characteristics) -> List[str]:
    """Identify limitations for descriptive analysis."""
    limitations = []
    
    if characteristics.n_observations < 30:
        limitations.append("Small sample size limits statistical reliability")
    if characteristics.missing_percentage > 30:
        limitations.append("High missing data may bias results")
    if characteristics.n_variables < 2:
        limitations.append("Single variable limits relationship analysis")
    
    return limitations

def _get_data_improvement_recommendations(characteristics) -> List[str]:
    """Get recommendations for improving data for analysis."""
    recommendations = []
    
    if characteristics.missing_percentage > 20:
        recommendations.append("Address missing data through imputation or collection")
    if characteristics.n_observations < 100:
        recommendations.append("Increase sample size for more robust analysis")
    if characteristics.duplicate_rows > 0:
        recommendations.append("Remove duplicate observations")
    if not characteristics.grouping_variables:
        recommendations.append("Consider adding categorical variables for grouping analysis")
    
    return recommendations

def _explain_descriptive_parameters(method_name: str, config: Dict[str, Any]) -> Dict[str, str]:
    """Explain parameters for descriptive methods."""
    explanations = {
        "basic_statistics": {
            "target_columns": "Variables to analyze for basic statistics",
            "include_percentiles": "Whether to include percentile calculations",
            "confidence_level": "Confidence level for confidence intervals",
            "grouping_variables": "Variables to group analysis by"
        },
        "distribution_analysis": {
            "target_columns": "Variables to analyze for distribution properties",
            "normality_tests": "Statistical tests for normality assessment",
            "distribution_fitting": "Whether to fit theoretical distributions",
            "plot_distributions": "Whether to create distribution plots"
        },
        "correlation_analysis": {
            "method": "Correlation method (pearson, spearman, kendall)",
            "min_periods": "Minimum number of observations for correlation",
            "significance_testing": "Whether to test correlation significance"
        }
    }
    
    method_explanations = explanations.get(method_name, {})
    return {param: method_explanations.get(param, f"Parameter for {method_name}") 
            for param in config.keys() if param != "analysis_type"}

def _get_descriptive_execution_guidance(method_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Get execution guidance for descriptive methods."""
    base_guidance = {
        "recommended_order": 1,
        "prerequisites": [],
        "expected_output": "Statistical summary and insights",
        "interpretation_notes": "Focus on data patterns and distributions"
    }
    
    method_specific = {
        "basic_statistics": {
            "recommended_order": 1,
            "prerequisites": ["data_cleaning"],
            "expected_output": "Mean, median, mode, standard deviation, etc.",
            "interpretation_notes": "Start with basic statistics to understand data center and spread"
        },
        "distribution_analysis": {
            "recommended_order": 2,
            "prerequisites": ["basic_statistics"],
            "expected_output": "Normality tests, distribution plots, skewness/kurtosis",
            "interpretation_notes": "Assess data distribution shape and normality assumptions"
        },
        "correlation_analysis": {
            "recommended_order": 3,
            "prerequisites": ["basic_statistics", "distribution_analysis"],
            "expected_output": "Correlation matrix, significance tests",
            "interpretation_notes": "Identify linear relationships between variables"
        }
    }
    
    return method_specific.get(method_name, base_guidance)

def _get_recommendation_rationale(df: pd.DataFrame, recommendation: str) -> str:
    """Get rationale for quick recommendation."""
    rationales = {
        "basic_statistics": f"Dataset has {len(df)} observations and {len(df.columns)} variables - basic statistics provide essential data overview",
        "correlation_analysis": f"Multiple numeric variables detected - correlation analysis reveals relationships",
        "categorical_analysis": f"Categorical variables present - frequency analysis recommended",
        "missing_data_analysis": f"Missing data detected - quality assessment needed"
    }
    
    return rationales.get(recommendation.split('+')[0].strip(), "Recommended based on data characteristics")

def _estimate_analysis_time(recommendation: str, sample_size: int) -> str:
    """Estimate analysis execution time."""
    base_times = {
        "basic_statistics": 1,
        "correlation_analysis": 5,
        "categorical_analysis": 3,
        "distribution_analysis": 8,
        "missing_data_analysis": 2
    }
    
    methods = recommendation.split('+')
    total_time = sum(base_times.get(method.strip(), 3) for method in methods)
    
    # Adjust for sample size
    if sample_size > 10000:
        total_time *= 2
    elif sample_size > 100000:
        total_time *= 5
    
    if total_time < 10:
        return "< 10 seconds"
    elif total_time < 60:
        return "< 1 minute"
    else:
        return f"~ {total_time // 60} minutes"

def _get_next_steps(recommendation: str) -> List[str]:
    """Get next steps after analysis."""
    steps = [
        "Execute the recommended analysis",
        "Review results and identify patterns",
        "Check for data quality issues",
        "Consider additional analyses based on findings"
    ]
    
    if "correlation" in recommendation:
        steps.append("Investigate strong correlations for potential causation")
    if "missing_data" in recommendation:
        steps.append("Develop strategy for handling missing data")
    
    return steps

def _categorize_descriptive_methods(methods: Dict[str, Any]) -> Dict[str, List[str]]:
    """Categorize descriptive methods by type."""
    return {
        "basic_analysis": ["basic_statistics", "missing_data_analysis"],
        "distribution_analysis": ["distribution_analysis", "outlier_detection"],
        "relationship_analysis": ["correlation_analysis", "cross_tabulation"],
        "specialized_analysis": ["temporal_analysis", "geospatial_analysis", "grouped_analysis"],
        "categorical_analysis": ["categorical_analysis", "cross_tabulation"]
    }

def _get_usage_guidelines() -> Dict[str, str]:
    """Get usage guidelines for descriptive methods."""
    return {
        "basic_statistics": "Use for initial data exploration and summary statistics",
        "distribution_analysis": "Use to understand data distribution and check normality",
        "correlation_analysis": "Use to identify relationships between numeric variables",
        "categorical_analysis": "Use to analyze frequency distributions of categorical data",
        "outlier_detection": "Use to identify unusual observations that may need attention",
        "missing_data_analysis": "Use to assess data completeness and missing patterns"
    }

def _get_visualization_recommendations(df: pd.DataFrame) -> List[Dict[str, str]]:
    """Get visualization recommendations for descriptive analysis."""
    recommendations = []
    
    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    
    if len(numeric_cols) > 0:
        recommendations.append({
            "type": "histogram",
            "purpose": "Show distribution of numeric variables",
            "variables": list(numeric_cols[:5])
        })
    
    if len(numeric_cols) >= 2:
        recommendations.append({
            "type": "correlation_heatmap",
            "purpose": "Visualize correlations between numeric variables",
            "variables": list(numeric_cols)
        })
    
    if len(categorical_cols) > 0:
        recommendations.append({
            "type": "bar_chart",
            "purpose": "Show frequency of categorical variables",
            "variables": list(categorical_cols[:3])
        })
    
    return recommendations
