"""
Inferential statistics module for research data analysis.
"""

from .hypothesis_testing import (
    perform_t_test,
    perform_paired_t_test,
    perform_welch_t_test,
    perform_anova,
    perform_two_way_anova,
    perform_repeated_measures_anova,
    perform_chi_square_test,
    perform_fisher_exact_test,
    perform_mcnemar_test,
    perform_correlation_test,
    perform_partial_correlation,
    hypothesis_test_summary
)

from .confidence_intervals import (
    calculate_mean_ci,
    calculate_proportion_ci,
    calculate_difference_ci,
    calculate_correlation_ci,
    calculate_median_ci,
    calculate_bootstrap_ci,
    calculate_prediction_interval
)

from .power_analysis import (
    calculate_sample_size_t_test,
    calculate_sample_size_anova,
    calculate_sample_size_proportion,
    calculate_sample_size_correlation,
    calculate_power_t_test,
    calculate_power_anova,
    calculate_effect_size_needed,
    post_hoc_power_analysis
)

from .effect_sizes import (
    calculate_cohens_d,
    calculate_hedges_g,
    calculate_glass_delta,
    calculate_eta_squared,
    calculate_omega_squared,
    calculate_cohens_f,
    calculate_cramers_v,
    calculate_odds_ratio,
    calculate_risk_ratio,
    calculate_nnt
)

from .multiple_comparisons import (
    bonferroni_correction,
    holm_bonferroni_correction,
    benjamini_hochberg_correction,
    benjamini_yekutieli_correction,
    tukey_hsd_test,
    dunnett_test,
    games_howell_test
)

from .nonparametric_tests import (
    mann_whitney_u_test,
    wilcoxon_signed_rank_test,
    kruskal_wallis_test,
    friedman_test,
    runs_test,
    kolmogorov_smirnov_test,
    anderson_darling_test,
    shapiro_wilk_test,
    mood_median_test
)

from .regression_analysis import (
    perform_linear_regression,
    perform_multiple_regression,
    perform_logistic_regression,
    perform_poisson_regression,
    calculate_regression_diagnostics,
    calculate_vif,
    perform_ridge_regression,
    perform_lasso_regression,
    perform_robust_regression
)

from .time_series_inference import (
    test_stationarity,
    test_autocorrelation,
    test_seasonality,
    granger_causality_test,
    cointegration_test,
    change_point_detection,
    forecast_accuracy_tests
)

from .bayesian_inference import (
    bayesian_t_test,
    bayesian_proportion_test,
    calculate_bayes_factor,
    calculate_posterior_distribution,
    calculate_credible_interval,
    bayesian_ab_test
)

from .bootstrap_methods import (
    bootstrap_mean,
    bootstrap_median,
    bootstrap_correlation,
    bootstrap_regression,
    permutation_test,
    jackknife_estimate,
    bootstrap_hypothesis_test
)

__all__ = [
    # Hypothesis Testing
    'perform_t_test', 'perform_paired_t_test', 'perform_welch_t_test',
    'perform_anova', 'perform_two_way_anova', 'perform_repeated_measures_anova',
    'perform_chi_square_test', 'perform_fisher_exact_test', 'perform_mcnemar_test',
    'perform_correlation_test', 'perform_partial_correlation', 'hypothesis_test_summary',
    
    # Confidence Intervals
    'calculate_mean_ci', 'calculate_proportion_ci', 'calculate_difference_ci',
    'calculate_correlation_ci', 'calculate_median_ci', 'calculate_bootstrap_ci',
    'calculate_prediction_interval',
    
    # Power Analysis
    'calculate_sample_size_t_test', 'calculate_sample_size_anova',
    'calculate_sample_size_proportion', 'calculate_sample_size_correlation',
    'calculate_power_t_test', 'calculate_power_anova', 'calculate_effect_size_needed',
    'post_hoc_power_analysis',
    
    # Effect Sizes
    'calculate_cohens_d', 'calculate_hedges_g', 'calculate_glass_delta',
    'calculate_eta_squared', 'calculate_omega_squared', 'calculate_cohens_f',
    'calculate_cramers_v', 'calculate_odds_ratio', 'calculate_risk_ratio',
    'calculate_nnt',
    
    # Multiple Comparisons
    'bonferroni_correction', 'holm_bonferroni_correction',
    'benjamini_hochberg_correction', 'benjamini_yekutieli_correction',
    'tukey_hsd_test', 'dunnett_test', 'games_howell_test',
    
    # Non-parametric Tests
    'mann_whitney_u_test', 'wilcoxon_signed_rank_test', 'kruskal_wallis_test',
    'friedman_test', 'runs_test', 'kolmogorov_smirnov_test',
    'anderson_darling_test', 'shapiro_wilk_test', 'mood_median_test',
    
    # Regression Analysis
    'perform_linear_regression', 'perform_multiple_regression',
    'perform_logistic_regression', 'perform_poisson_regression',
    'calculate_regression_diagnostics', 'calculate_vif',
    'perform_ridge_regression', 'perform_lasso_regression', 'perform_robust_regression',
    
    # Time Series Inference
    'test_stationarity', 'test_autocorrelation', 'test_seasonality',
    'granger_causality_test', 'cointegration_test', 'change_point_detection',
    'forecast_accuracy_tests',
    
    # Bayesian Inference
    'bayesian_t_test', 'bayesian_proportion_test', 'calculate_bayes_factor',
    'calculate_posterior_distribution', 'calculate_credible_interval',
    'bayesian_ab_test',
    
    # Bootstrap Methods
    'bootstrap_mean', 'bootstrap_median', 'bootstrap_correlation',
    'bootstrap_regression', 'permutation_test', 'jackknife_estimate',
    'bootstrap_hypothesis_test'
]