"""
Inferential analytics endpoints with auto-detection capabilities.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import json

from core.database import get_db
from app.analytics.inferential.auto_detection import (
    InferentialAutoDetector,
    auto_detect_statistical_tests,
    quick_test_suggestion
)
from app.analytics.auto_detect.base_detector import DataType

router = APIRouter()

@router.post("/analyze")
async def analyze_inferential(
    data: Dict[str, Any],
    target_variable: Optional[str] = None,
    grouping_variable: Optional[str] = None,
    research_question: Optional[str] = None,
    alpha: float = 0.05,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform comprehensive inferential analysis with auto-detection.
    
    Args:
        data: Input data as a dictionary
        target_variable: Dependent variable name
        grouping_variable: Independent/grouping variable name
        research_question: Type of research question
        alpha: Significance level
        db: Database session
        
    Returns:
        Comprehensive inferential analysis results
    """
    try:
        df = pd.DataFrame(data)
        
        # Use the auto-analysis function
        results = auto_detect_statistical_tests(
            df,
            target_variable=target_variable,
            grouping_variable=grouping_variable,
            research_question=research_question,
            alpha=alpha
        )
        
        # Format for API response
        return {
            "status": "success",
            "analysis_type": "inferential",
            "data_overview": _format_data_overview(results["data_characteristics"]),
            "test_recommendations": _format_test_suggestions(results["test_suggestions"]),
            "research_design": _format_research_design(results["data_characteristics"], target_variable, grouping_variable),
            "auto_configuration": results["auto_configuration"],
            "analysis_report": results["analysis_report"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error in inferential analysis: {str(e)}"
        )

@router.post("/suggest-tests")
async def suggest_statistical_tests(
    data: Dict[str, Any],
    target_variable: Optional[str] = None,
    grouping_variable: Optional[str] = None,
    research_question: Optional[str] = None,
    alpha: float = 0.05,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get statistical test suggestions for inferential analysis.
    
    Args:
        data: Input data as a dictionary
        target_variable: Dependent variable name
        grouping_variable: Independent variable name
        research_question: Type of research question
        alpha: Significance level
        db: Database session
        
    Returns:
        Statistical test suggestions and recommendations
    """
    try:
        df = pd.DataFrame(data)
        detector = InferentialAutoDetector()
        
        suggestions = detector.suggest_statistical_tests(
            df,
            target_variable=target_variable,
            grouping_variable=grouping_variable,
            research_question=research_question,
            alpha=alpha
        )
        
        characteristics = detector.detect_data_characteristics(df, target_variable, grouping_variable)
        
        return {
            "status": "success",
            "data_characteristics": _format_data_characteristics(characteristics),
            "primary_recommendations": suggestions["primary_recommendations"],
            "secondary_recommendations": suggestions["secondary_recommendations"],
            "not_recommended": suggestions["not_recommended"],
            "power_analysis_needed": suggestions["power_analysis_needed"],
            "sample_size_recommendations": suggestions["sample_size_recommendations"],
            "assumption_violations": suggestions["assumption_violations"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error suggesting tests: {str(e)}"
        )

@router.post("/configure-test/{method_name}")
async def configure_statistical_test(
    method_name: str,
    data: Dict[str, Any],
    target_variable: Optional[str] = None,
    grouping_variable: Optional[str] = None,
    custom_parameters: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Auto-configure parameters for a specific statistical test.
    
    Args:
        method_name: Name of the statistical test
        data: Input data as a dictionary
        target_variable: Dependent variable
        grouping_variable: Independent variable
        custom_parameters: Optional custom parameter overrides
        db: Database session
        
    Returns:
        Optimized configuration for the test
    """
    try:
        df = pd.DataFrame(data)
        detector = InferentialAutoDetector()
        
        config = detector.auto_configure_test(
            method_name,
            df,
            target_variable=target_variable,
            grouping_variable=grouping_variable
        )
        
        # Apply custom parameter overrides
        if custom_parameters:
            config.update(custom_parameters)
        
        return {
            "method": method_name,
            "configuration": config,
            "parameter_explanation": _explain_test_parameters(method_name, config),
            "execution_guidance": _get_test_execution_guidance(method_name, config),
            "assumption_checks": _get_assumption_checks(method_name)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error configuring test {method_name}: {str(e)}"
        )

@router.post("/data-characteristics")
async def get_inferential_data_characteristics(
    data: Dict[str, Any],
    target_variable: Optional[str] = None,
    grouping_variable: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed data characteristics for inferential analysis.
    
    Args:
        data: Input data as a dictionary
        target_variable: Target variable
        grouping_variable: Grouping variable
        db: Database session
        
    Returns:
        Detailed data characteristics and statistical assumptions
    """
    try:
        df = pd.DataFrame(data)
        detector = InferentialAutoDetector()
        
        characteristics = detector.detect_data_characteristics(df, target_variable, grouping_variable)
        
        return {
            "status": "success",
            "data_profile": _format_data_characteristics(characteristics),
            "variable_analysis": _analyze_variables_inferential(characteristics, df, target_variable, grouping_variable),
            "assumption_testing": _test_statistical_assumptions(df, target_variable, grouping_variable),
            "power_analysis": _assess_statistical_power(characteristics),
            "recommendations": _get_inferential_recommendations(characteristics)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error analyzing data characteristics: {str(e)}"
        )

@router.post("/quick-test-suggestion")
async def get_quick_test_suggestion(
    data1: List[Union[int, float]],
    data2: Optional[List[Union[int, float]]] = None,
    paired: bool = False,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get quick test suggestion for one or two samples.
    
    Args:
        data1: First sample data
        data2: Second sample data (optional)
        paired: Whether samples are paired
        db: Database session
        
    Returns:
        Quick test recommendation
    """
    try:
        series1 = pd.Series(data1)
        series2 = pd.Series(data2) if data2 is not None else None
        
        recommendation = quick_test_suggestion(series1, series2, paired)
        
        return {
            "status": "success",
            "recommendation": recommendation,
            "rationale": _get_test_rationale(series1, series2, paired),
            "sample_info": _get_sample_info(series1, series2),
            "next_steps": _get_test_next_steps(recommendation)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error getting quick test suggestion: {str(e)}"
        )

@router.post("/check-assumptions")
async def check_test_assumptions(
    data: Dict[str, Any],
    test_name: str,
    target_variable: Optional[str] = None,
    grouping_variable: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Check statistical assumptions for a specific test.
    
    Args:
        data: Input data as a dictionary
        test_name: Name of the statistical test
        target_variable: Target variable
        grouping_variable: Grouping variable
        db: Database session
        
    Returns:
        Assumption check results
    """
    try:
        df = pd.DataFrame(data)
        
        assumption_results = _perform_assumption_checks(df, test_name, target_variable, grouping_variable)
        
        return {
            "status": "success",
            "test_name": test_name,
            "assumption_results": assumption_results,
            "overall_assessment": _assess_assumptions_overall(assumption_results),
            "recommendations": _get_assumption_recommendations(assumption_results),
            "alternative_tests": _suggest_alternative_tests(assumption_results, test_name)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error checking assumptions: {str(e)}"
        )

@router.get("/methods")
async def list_inferential_methods(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    List all available inferential analysis methods.
    
    Returns:
        Dictionary of available methods with requirements
    """
    try:
        detector = InferentialAutoDetector()
        methods = detector.get_method_requirements()
        
        return {
            "status": "success",
            "methods": methods,
            "method_categories": _categorize_inferential_methods(methods),
            "assumption_guide": _get_assumption_guide(),
            "usage_guidelines": _get_inferential_usage_guidelines()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing methods: {str(e)}"
        )

@router.post("/generate-report")
async def generate_inferential_report(
    data: Dict[str, Any],
    target_variable: Optional[str] = None,
    grouping_variable: Optional[str] = None,
    include_assumptions: bool = True,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate a comprehensive inferential analysis report.
    
    Args:
        data: Input data as a dictionary
        target_variable: Target variable
        grouping_variable: Grouping variable
        include_assumptions: Whether to include assumption testing
        db: Database session
        
    Returns:
        Comprehensive analysis report
    """
    try:
        df = pd.DataFrame(data)
        detector = InferentialAutoDetector()
        
        report = detector.generate_analysis_report(df, target_variable, grouping_variable)
        
        response = {
            "status": "success",
            "report": report,
            "metadata": {
                "generated_at": pd.Timestamp.now().isoformat(),
                "data_shape": df.shape,
                "analysis_type": "inferential",
                "target_variable": target_variable,
                "grouping_variable": grouping_variable
            }
        }
        
        if include_assumptions:
            response["assumption_testing"] = _test_statistical_assumptions(df, target_variable, grouping_variable)
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error generating report: {str(e)}"
        )

# Helper functions for inferential analytics endpoints

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

def _format_test_suggestions(suggestions) -> Dict[str, Any]:
    """Format test suggestions for API response."""
    return {
        "primary_recommendations": suggestions["primary_recommendations"],
        "secondary_recommendations": suggestions["secondary_recommendations"],
        "not_recommended": suggestions["not_recommended"],
        "power_analysis_needed": suggestions["power_analysis_needed"],
        "sample_size_recommendations": suggestions["sample_size_recommendations"],
        "assumption_violations": suggestions["assumption_violations"]
    }

def _format_research_design(characteristics, target_variable: Optional[str], grouping_variable: Optional[str]) -> Dict[str, Any]:
    """Format research design information."""
    design_info = {
        "design_type": "experimental" if target_variable and grouping_variable else "observational",
        "comparison_type": "between_groups" if grouping_variable else "single_group",
        "variable_roles": {
            "dependent": target_variable,
            "independent": grouping_variable
        }
    }
    
    if grouping_variable and hasattr(characteristics, 'variable_types'):
        # Estimate number of groups if we have the data
        design_info["estimated_groups"] = "multiple"
    
    return design_info

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
        "statistical_readiness": {
            "sample_size_category": characteristics.sample_size_category,
            "sufficient_for_inference": characteristics.n_observations >= 30
        }
    }

def _analyze_variables_inferential(characteristics, df: pd.DataFrame, target_variable: Optional[str], grouping_variable: Optional[str]) -> Dict[str, Any]:
    """Analyze variables for inferential statistics."""
    analysis = {
        "target_variable_analysis": {},
        "grouping_variable_analysis": {},
        "relationship_potential": {}
    }
    
    if target_variable and target_variable in df.columns:
        target_data = df[target_variable].dropna()
        analysis["target_variable_analysis"] = {
            "type": _classify_variable_type(target_data),
            "sample_size": len(target_data),
            "missing_count": df[target_variable].isna().sum(),
            "unique_values": target_data.nunique()
        }
        
        if pd.api.types.is_numeric_dtype(target_data):
            analysis["target_variable_analysis"]["statistics"] = {
                "mean": float(target_data.mean()),
                "std": float(target_data.std()),
                "median": float(target_data.median()),
                "skewness": float(target_data.skew())
            }
    
    if grouping_variable and grouping_variable in df.columns:
        group_data = df[grouping_variable].dropna()
        analysis["grouping_variable_analysis"] = {
            "type": _classify_variable_type(group_data),
            "unique_groups": group_data.nunique(),
            "group_sizes": group_data.value_counts().to_dict(),
            "missing_count": df[grouping_variable].isna().sum()
        }
    
    # Assess relationship potential
    if target_variable and grouping_variable:
        analysis["relationship_potential"] = {
            "suitable_for_comparison": True,
            "recommended_tests": _suggest_tests_for_variables(df, target_variable, grouping_variable)
        }
    
    return analysis

def _classify_variable_type(series: pd.Series) -> str:
    """Classify variable type for statistical analysis."""
    if pd.api.types.is_numeric_dtype(series):
        unique_vals = series.nunique()
        if unique_vals == 2:
            return "binary"
        elif unique_vals > 20:
            return "continuous"
        else:
            return "discrete"
    else:
        return "categorical"

def _suggest_tests_for_variables(df: pd.DataFrame, target_var: str, group_var: str) -> List[str]:
    """Suggest appropriate tests based on variable types."""
    target_type = _classify_variable_type(df[target_var].dropna())
    group_type = _classify_variable_type(df[group_var].dropna())
    n_groups = df[group_var].nunique()
    
    suggestions = []
    
    if target_type in ["continuous", "discrete"] and group_type == "categorical":
        if n_groups == 2:
            suggestions.extend(["two_sample_t_test", "mann_whitney_u"])
        elif n_groups > 2:
            suggestions.extend(["one_way_anova", "kruskal_wallis"])
    
    if target_type == "categorical" and group_type == "categorical":
        suggestions.append("chi_square_independence")
    
    return suggestions

def _test_statistical_assumptions(df: pd.DataFrame, target_variable: Optional[str], grouping_variable: Optional[str]) -> Dict[str, Any]:
    """Test statistical assumptions for the data."""
    assumptions = {
        "normality": {},
        "equal_variances": {},
        "independence": {"status": "assumed", "note": "Cannot test independence from data alone"}
    }
    
    if target_variable and target_variable in df.columns:
        target_data = df[target_variable].dropna()
        if pd.api.types.is_numeric_dtype(target_data) and len(target_data) >= 3:
            from scipy import stats
            
            # Test normality
            if len(target_data) <= 5000:  # Shapiro-Wilk for smaller samples
                stat, p_value = stats.shapiro(target_data)
                assumptions["normality"] = {
                    "test": "shapiro_wilk",
                    "statistic": float(stat),
                    "p_value": float(p_value),
                    "assumption_met": p_value > 0.05
                }
            else:  # Kolmogorov-Smirnov for larger samples
                stat, p_value = stats.kstest(target_data, 'norm')
                assumptions["normality"] = {
                    "test": "kolmogorov_smirnov",
                    "statistic": float(stat),
                    "p_value": float(p_value),
                    "assumption_met": p_value > 0.05
                }
    
    # Test equal variances if we have groups
    if (target_variable and grouping_variable and 
        target_variable in df.columns and grouping_variable in df.columns):
        
        groups = df.groupby(grouping_variable)[target_variable].apply(lambda x: x.dropna())
        if len(groups) >= 2:
            group_list = [group for _, group in groups if len(group) >= 2]
            if len(group_list) >= 2:
                from scipy import stats
                stat, p_value = stats.levene(*group_list)
                assumptions["equal_variances"] = {
                    "test": "levene",
                    "statistic": float(stat),
                    "p_value": float(p_value),
                    "assumption_met": p_value > 0.05
                }
    
    return assumptions

def _assess_statistical_power(characteristics) -> Dict[str, Any]:
    """Assess statistical power based on sample size."""
    sample_size = characteristics.n_observations
    
    power_assessment = {
        "sample_size": sample_size,
        "power_level": "adequate" if sample_size >= 30 else "low",
        "recommendations": []
    }
    
    if sample_size < 30:
        power_assessment["recommendations"].append("Consider increasing sample size for adequate power")
        power_assessment["minimum_recommended"] = 30
    
    if sample_size < 80:
        power_assessment["recommendations"].append("Sample size may be insufficient for detecting small effect sizes")
    
    return power_assessment

def _get_inferential_recommendations(characteristics) -> List[str]:
    """Get recommendations for inferential analysis."""
    recommendations = []
    
    if characteristics.n_observations < 30:
        recommendations.append("Increase sample size for more reliable statistical inference")
    
    if characteristics.missing_percentage > 10:
        recommendations.append("Address missing data before conducting statistical tests")
    
    if characteristics.duplicate_rows > 0:
        recommendations.append("Remove duplicate observations to avoid biased results")
    
    return recommendations

def _perform_assumption_checks(df: pd.DataFrame, test_name: str, target_variable: Optional[str], grouping_variable: Optional[str]) -> Dict[str, Any]:
    """Perform assumption checks for a specific test."""
    results = {}
    
    test_assumptions = {
        "one_sample_t_test": ["normality"],
        "two_sample_t_test": ["normality", "equal_variances"],
        "paired_t_test": ["normality_differences"],
        "one_way_anova": ["normality", "equal_variances"],
        "correlation_test": ["bivariate_normality"]
    }
    
    required_assumptions = test_assumptions.get(test_name, [])
    
    for assumption in required_assumptions:
        if assumption == "normality":
            results[assumption] = _test_normality(df, target_variable)
        elif assumption == "equal_variances":
            results[assumption] = _test_equal_variances(df, target_variable, grouping_variable)
        else:
            results[assumption] = {"status": "not_tested", "note": f"Test for {assumption} not implemented"}
    
    return results

def _test_normality(df: pd.DataFrame, target_variable: Optional[str]) -> Dict[str, Any]:
    """Test normality assumption."""
    if not target_variable or target_variable not in df.columns:
        return {"status": "cannot_test", "reason": "Target variable not specified or not found"}
    
    data = df[target_variable].dropna()
    if len(data) < 3:
        return {"status": "insufficient_data", "reason": "Need at least 3 observations"}
    
    from scipy import stats
    
    if len(data) <= 5000:
        stat, p_value = stats.shapiro(data)
        return {
            "test": "shapiro_wilk",
            "statistic": float(stat),
            "p_value": float(p_value),
            "assumption_met": p_value > 0.05,
            "interpretation": "Normal" if p_value > 0.05 else "Not normal"
        }
    else:
        stat, p_value = stats.kstest(data, 'norm')
        return {
            "test": "kolmogorov_smirnov",
            "statistic": float(stat),
            "p_value": float(p_value),
            "assumption_met": p_value > 0.05,
            "interpretation": "Normal" if p_value > 0.05 else "Not normal"
        }

def _test_equal_variances(df: pd.DataFrame, target_variable: Optional[str], grouping_variable: Optional[str]) -> Dict[str, Any]:
    """Test equal variances assumption."""
    if not all([target_variable, grouping_variable]) or not all([var in df.columns for var in [target_variable, grouping_variable]]):
        return {"status": "cannot_test", "reason": "Both target and grouping variables needed"}
    
    groups = df.groupby(grouping_variable)[target_variable].apply(lambda x: x.dropna())
    group_list = [group for _, group in groups if len(group) >= 2]
    
    if len(group_list) < 2:
        return {"status": "insufficient_groups", "reason": "Need at least 2 groups with 2+ observations each"}
    
    from scipy import stats
    stat, p_value = stats.levene(*group_list)
    
    return {
        "test": "levene",
        "statistic": float(stat),
        "p_value": float(p_value),
        "assumption_met": p_value > 0.05,
        "interpretation": "Equal variances" if p_value > 0.05 else "Unequal variances"
    }

def _assess_assumptions_overall(assumption_results: Dict[str, Any]) -> Dict[str, Any]:
    """Assess overall assumption status."""
    met_count = sum(1 for result in assumption_results.values() 
                   if isinstance(result, dict) and result.get("assumption_met", False))
    total_tested = sum(1 for result in assumption_results.values() 
                      if isinstance(result, dict) and "assumption_met" in result)
    
    if total_tested == 0:
        status = "not_tested"
        recommendation = "No assumptions could be tested"
    elif met_count == total_tested:
        status = "all_met"
        recommendation = "All assumptions satisfied - proceed with test"
    elif met_count >= total_tested / 2:
        status = "mostly_met"
        recommendation = "Most assumptions satisfied - test may still be appropriate"
    else:
        status = "violated"
        recommendation = "Key assumptions violated - consider alternative tests"
    
    return {
        "status": status,
        "met_count": met_count,
        "total_tested": total_tested,
        "recommendation": recommendation
    }

def _get_assumption_recommendations(assumption_results: Dict[str, Any]) -> List[str]:
    """Get recommendations based on assumption results."""
    recommendations = []
    
    for assumption, result in assumption_results.items():
        if isinstance(result, dict) and not result.get("assumption_met", True):
            if assumption == "normality":
                recommendations.append("Consider non-parametric tests due to non-normal distribution")
            elif assumption == "equal_variances":
                recommendations.append("Use Welch's t-test or robust variance tests")
    
    return recommendations

def _suggest_alternative_tests(assumption_results: Dict[str, Any], original_test: str) -> List[str]:
    """Suggest alternative tests when assumptions are violated."""
    alternatives = []
    
    violated_assumptions = [assumption for assumption, result in assumption_results.items()
                           if isinstance(result, dict) and not result.get("assumption_met", True)]
    
    if "normality" in violated_assumptions:
        test_alternatives = {
            "one_sample_t_test": ["wilcoxon_signed_rank"],
            "two_sample_t_test": ["mann_whitney_u"],
            "paired_t_test": ["wilcoxon_signed_rank"],
            "one_way_anova": ["kruskal_wallis"]
        }
        alternatives.extend(test_alternatives.get(original_test, []))
    
    if "equal_variances" in violated_assumptions:
        if original_test == "two_sample_t_test":
            alternatives.append("welch_t_test")
    
    return list(set(alternatives))  # Remove duplicates

def _explain_test_parameters(method_name: str, config: Dict[str, Any]) -> Dict[str, str]:
    """Explain parameters for statistical tests."""
    explanations = {
        "alpha": "Significance level (probability of Type I error)",
        "alternative": "Type of alternative hypothesis (two-sided, greater, less)",
        "equal_var": "Whether to assume equal variances between groups",
        "confidence_level": "Confidence level for confidence intervals",
        "correction": "Whether to apply continuity correction",
        "method": "Specific method variant to use"
    }
    
    return {param: explanations.get(param, f"Parameter for {method_name}") 
            for param in config.keys() if param != "test_type"}

def _get_test_execution_guidance(method_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Get execution guidance for statistical tests."""
    guidance = {
        "prerequisites": ["assumption_checking", "data_cleaning"],
        "expected_output": "Test statistic, p-value, confidence interval",
        "interpretation_notes": "Compare p-value to alpha level",
        "post_analysis": ["effect_size_calculation", "confidence_intervals"]
    }
    
    method_specific = {
        "one_sample_t_test": {
            "prerequisites": ["normality_check"],
            "interpretation_notes": "Test if mean differs significantly from hypothesized value"
        },
        "two_sample_t_test": {
            "prerequisites": ["normality_check", "equal_variance_check"],
            "interpretation_notes": "Test if means of two groups differ significantly"
        },
        "mann_whitney_u": {
            "prerequisites": ["data_cleaning"],
            "interpretation_notes": "Non-parametric test for difference in distributions"
        }
    }
    
    guidance.update(method_specific.get(method_name, {}))
    return guidance

def _get_assumption_checks(method_name: str) -> List[str]:
    """Get required assumption checks for a test."""
    test_assumptions = {
        "one_sample_t_test": ["normality"],
        "two_sample_t_test": ["normality", "equal_variances"],
        "paired_t_test": ["normality_differences"],
        "welch_t_test": ["normality"],
        "mann_whitney_u": [],
        "wilcoxon_signed_rank": [],
        "one_way_anova": ["normality", "equal_variances"],
        "kruskal_wallis": [],
        "chi_square_independence": ["expected_frequencies"],
        "correlation_test": ["bivariate_normality"]
    }
    
    return test_assumptions.get(method_name, [])

def _get_test_rationale(series1: pd.Series, series2: Optional[pd.Series], paired: bool) -> str:
    """Get rationale for quick test suggestion."""
    n1 = len(series1.dropna())
    
    if series2 is None:
        return f"Single sample with n={n1} - appropriate test depends on distribution and sample size"
    else:
        n2 = len(series2.dropna())
        if paired:
            return f"Paired samples with n={min(n1, n2)} - test accounts for pairing structure"
        else:
            return f"Independent samples with n1={n1}, n2={n2} - test compares group differences"

def _get_sample_info(series1: pd.Series, series2: Optional[pd.Series]) -> Dict[str, Any]:
    """Get sample information for test suggestion."""
    info = {
        "sample1": {
            "size": len(series1.dropna()),
            "mean": float(series1.mean()),
            "std": float(series1.std())
        }
    }
    
    if series2 is not None:
        info["sample2"] = {
            "size": len(series2.dropna()),
            "mean": float(series2.mean()),
            "std": float(series2.std())
        }
    
    return info

def _get_test_next_steps(recommendation: str) -> List[str]:
    """Get next steps after test recommendation."""
    steps = [
        "Check statistical assumptions for the recommended test",
        "Prepare data (handle missing values, outliers)",
        "Execute the statistical test",
        "Interpret results in context of research question"
    ]
    
    if "bootstrap" in recommendation:
        steps.insert(-1, "Set random seed for reproducibility")
    
    if "non-parametric" in recommendation or "mann_whitney" in recommendation:
        steps[0] = "Minimal assumptions - proceed with data preparation"
    
    return steps

def _categorize_inferential_methods(methods: Dict[str, Any]) -> Dict[str, List[str]]:
    """Categorize inferential methods by type."""
    return {
        "parametric_tests": ["one_sample_t_test", "two_sample_t_test", "paired_t_test", "one_way_anova"],
        "non_parametric_tests": ["mann_whitney_u", "wilcoxon_signed_rank", "kruskal_wallis"],
        "categorical_tests": ["chi_square_independence", "chi_square_goodness_of_fit", "fisher_exact"],
        "correlation_tests": ["correlation_test"],
        "regression_analysis": ["linear_regression", "logistic_regression"],
        "robust_methods": ["bootstrap_test", "welch_t_test"]
    }

def _get_assumption_guide() -> Dict[str, Dict[str, str]]:
    """Get guide for statistical assumptions."""
    return {
        "normality": {
            "description": "Data follows normal distribution",
            "how_to_check": "Shapiro-Wilk test, Q-Q plots, histograms",
            "violation_consequence": "Inflated Type I error rate",
            "alternatives": "Non-parametric tests, bootstrap methods"
        },
        "equal_variances": {
            "description": "Groups have equal variances",
            "how_to_check": "Levene's test, Bartlett's test",
            "violation_consequence": "Incorrect standard errors",
            "alternatives": "Welch's t-test, robust variance estimators"
        },
        "independence": {
            "description": "Observations are independent",
            "how_to_check": "Study design review, residual analysis",
            "violation_consequence": "Biased results and standard errors",
            "alternatives": "Mixed-effects models, clustered standard errors"
        }
    }

def _get_inferential_usage_guidelines() -> Dict[str, str]:
    """Get usage guidelines for inferential methods."""
    return {
        "one_sample_t_test": "Test if a sample mean differs from a known value",
        "two_sample_t_test": "Compare means of two independent groups",
        "paired_t_test": "Compare means of paired/matched observations",
        "mann_whitney_u": "Non-parametric comparison of two independent groups",
        "wilcoxon_signed_rank": "Non-parametric test for paired data",
        "one_way_anova": "Compare means of three or more groups",
        "chi_square_independence": "Test association between categorical variables",
        "correlation_test": "Test significance of correlation between variables"
    } 