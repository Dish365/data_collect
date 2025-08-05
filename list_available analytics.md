# Available Descriptive Analytics Functions

## Basic Statistics (`basic_statistics.py`)

### `calculate_basic_stats(df, columns=None)`
**Purpose:** Calculate comprehensive basic descriptive statistics for numerical columns
**Returns:** Dictionary containing statistics for each numerical column including:
- Central tendency: mean, median, mode, trimmed_mean_5
- Dispersion: std, variance, mad, iqr, range, cv (coefficient of variation)
- Position: min, max, q1, q3
- Shape: skewness, kurtosis
- Count statistics: count, missing_count, missing_percentage, unique_count, unique_percentage

### `calculate_percentiles(df, columns=None, percentiles=[0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99])`
**Purpose:** Calculate custom percentiles for numerical columns
**Returns:** Dictionary containing percentiles for each column (p1, p5, p10, etc.)

### `calculate_grouped_stats(df, group_by, target_columns=None, stats_functions=None)`
**Purpose:** Calculate statistics grouped by one or more categorical variables
**Returns:** DataFrame with grouped statistics including count, mean, std, min, max, median, cv, iqr

### `calculate_weighted_stats(df, value_column, weight_column)`
**Purpose:** Calculate weighted statistics using specified weight column
**Returns:** Dictionary containing weighted_mean, weighted_std, weighted_variance, weighted_median, total_weight, effective_sample_size

### `calculate_correlation_matrix(df, method='pearson', min_periods=1)`
**Purpose:** Calculate correlation matrix with multiple methods (pearson, kendall, spearman)
**Returns:** Correlation matrix as DataFrame

### `calculate_covariance_matrix(df, min_periods=1)`
**Purpose:** Calculate covariance matrix for numerical variables
**Returns:** Covariance matrix as DataFrame

## Categorical Analysis (`categorical_analysis.py`)

### `analyze_categorical(series, max_categories=50)`
**Purpose:** Comprehensive analysis of categorical data including frequencies, diversity metrics
**Returns:** Dictionary containing total_count, unique_categories, missing_count, mode, frequencies, diversity metrics

### `calculate_chi_square(df, var1, var2)`
**Purpose:** Perform chi-square test of independence between two categorical variables
**Returns:** Dictionary containing chi2_statistic, p_value, degrees_of_freedom, cramers_v, effect_size_interpretation, contingency_table, expected_frequencies

### `calculate_cramers_v(df, var1, var2)`
**Purpose:** Calculate Cramér's V statistic for association between categorical variables
**Returns:** Float value representing association strength (0-1)

### `analyze_cross_tabulation(df, var1, var2, normalize=None)`
**Purpose:** Create detailed cross-tabulation analysis with percentages and chi-square test
**Returns:** Dictionary containing crosstab, row_percentages, column_percentages, total_percentages, chi_square results

### `calculate_diversity_metrics(value_counts)`
**Purpose:** Calculate diversity metrics for categorical data (Shannon entropy, Simpson index, etc.)
**Returns:** Dictionary containing shannon_entropy, simpson_index, gini_simpson, evenness

### `analyze_categorical_associations(df, categorical_columns=None, method='cramers_v')`
**Purpose:** Calculate pairwise associations between all categorical variables
**Returns:** DataFrame with pairwise association measures

## Distribution Analysis (`distributions.py`)

### `analyze_distribution(series)`
**Purpose:** Comprehensive distribution analysis for numeric series
**Returns:** Dictionary containing distribution characteristics: n, mean, median, std, skewness, kurtosis, percentiles, shape_interpretation

### `test_normality(series, alpha=0.05)`
**Purpose:** Perform multiple normality tests (Shapiro-Wilk, D'Agostino-Pearson, Kolmogorov-Smirnov, Anderson-Darling)
**Returns:** Dictionary containing results from multiple normality tests with overall assessment

### `calculate_skewness_kurtosis(series)`
**Purpose:** Calculate detailed skewness and kurtosis metrics with statistical significance tests
**Returns:** Dictionary containing skewness and kurtosis values, standard errors, z-scores, significance tests, interpretations

### `fit_distribution(series, distributions=None)`
**Purpose:** Fit various distributions to data and find best fit using AIC criterion
**Returns:** Dictionary containing fit results for each distribution tested, with best_fit recommendation

## Geospatial Analysis (`geospatial_analysis.py`)

### `analyze_spatial_distribution(df, lat_column, lon_column, value_column=None)`
**Purpose:** Analyze spatial distribution of data points including clustering and hotspot analysis
**Returns:** Dictionary containing spatial statistics: total_points, bounding_box, center_point, spread, distance_stats, clusters, value_distribution

### `calculate_spatial_autocorrelation(df, lat_column, lon_column, value_column, max_distance_km=10)`
**Purpose:** Calculate Moran's I for spatial autocorrelation analysis
**Returns:** Dictionary containing morans_i, expected_i, interpretation, spatial correlation strength

### `create_location_clusters(df, lat_column, lon_column, n_clusters=5)`
**Purpose:** Create location-based clusters using K-means clustering
**Returns:** DataFrame with added location_cluster column

## Temporal Analysis (`temporal_analysis.py`)

### `analyze_temporal_patterns(df, date_column, value_columns=None)`
**Purpose:** Analyze temporal patterns including trends, seasonal patterns, and response timing
**Returns:** Dictionary containing date_range, temporal_statistics (daily/weekly/monthly aggregations), response_patterns, data_quality assessment

### `calculate_time_series_stats(series, date_index)`
**Purpose:** Calculate time series specific statistics including stationarity tests and autocorrelation
**Returns:** Dictionary containing length, frequency, stationarity tests (ADF, KPSS), autocorrelation at various lags

### `detect_seasonality(series, date_index, period=None)`
**Purpose:** Detect seasonality in time series data using seasonal decomposition
**Returns:** Dictionary containing period_used, seasonal_strength, has_seasonality, trend_strength, seasonal_peaks

---

# Available Qualitative Analytics Functions

## Content Analysis (`content_analysis.py`)

### `analyze_content_structure(texts)`
**Purpose:** Analyze structural characteristics of textual content (word count, sentence count, length distributions)
**Returns:** Dictionary containing document_count, total_words, avg_words_per_document, avg_sentences_per_document, word_length_distribution, document_length_distribution

### `analyze_content_categories(texts, custom_categories=None)`
**Purpose:** Analyze content based on predefined or custom word categories (emotional, action, descriptive words)
**Returns:** Dictionary containing category_statistics, document_category_presence, most_prominent_category

### `analyze_linguistic_features(texts)`
**Purpose:** Analyze linguistic characteristics including POS tags, lexical diversity, readability metrics
**Returns:** Dictionary containing pos_tag_distribution, lexical_diversity, total_unique_words, question_density, linguistic_complexity

### `analyze_content_patterns(texts)`
**Purpose:** Identify recurring patterns, n-grams, and phrase repetitions in textual content
**Returns:** Dictionary containing common_bigrams, common_trigrams, phrase_patterns, pattern_diversity

### `analyze_content_by_metadata(texts, metadata)`
**Purpose:** Analyze content patterns grouped by metadata categories (demographics, time periods, etc.)
**Returns:** Dictionary containing group_analysis with statistics for each metadata group

### `analyze_content_comprehensively(texts, metadata=None, custom_categories=None)`
**Purpose:** Perform comprehensive content analysis combining all content analysis methods
**Returns:** Dictionary containing structure_analysis, category_analysis, linguistic_analysis, pattern_analysis, metadata_analysis, summary report

## Qualitative Statistics (`qualitative_stats.py`)

### `calculate_basic_statistics(texts)`
**Purpose:** Calculate comprehensive descriptive statistics for qualitative text data
**Returns:** Dictionary containing document_statistics (word counts, lengths), vocabulary_statistics (lexical diversity, frequency distributions), distribution_statistics

### `calculate_data_quality_metrics(texts)`
**Purpose:** Assess quality and completeness of qualitative responses including missing data detection
**Returns:** Dictionary containing completeness metrics (response rates, empty responses), content_quality metrics (repetitive content, information richness), overall_quality_score

### `generate_comprehensive_summary(texts, metadata=None, analysis_type='general')`
**Purpose:** Generate comprehensive summary combining all qualitative statistics and quality metrics
**Returns:** Dictionary containing dataset_overview, content_summary, response_characteristics, key_insights, recommendations, detailed_statistics

### `generate_qualitative_report(texts, metadata=None, analysis_type='general')`
**Purpose:** Generate human-readable comprehensive report of qualitative data analysis
**Returns:** Formatted string report with overview, content summary, insights, and recommendations

## Sentiment Analysis (`sentiment.py`)

### `analyze_sentiment(text)`
**Purpose:** Analyze sentiment of individual text using polarity, subjectivity, and confidence measures
**Returns:** Dictionary containing polarity, subjectivity, confidence, magnitude, category, intensity

### `analyze_sentiment_batch(texts)`
**Purpose:** Perform sentiment analysis on multiple texts with batch processing
**Returns:** List of sentiment analysis dictionaries for each text

### `analyze_emotions(text)`
**Purpose:** Detect specific emotions (joy, anger, sadness, fear, surprise, disgust) using keyword matching
**Returns:** Dictionary containing emotion counts for each emotion category

### `analyze_sentiment_trends(texts, timestamps=None, categories=None)`
**Purpose:** Analyze sentiment trends over time and by categories with statistical summaries
**Returns:** Dictionary containing overall_statistics, category_distribution, intensity_distribution, daily_trends, category_analysis

### `analyze_sentiment_by_question(responses)`
**Purpose:** Analyze sentiment for responses grouped by survey questions with comparative statistics
**Returns:** Dictionary containing sentiment analysis for each question with statistics and representative responses

### `detect_sentiment_patterns(texts)`
**Purpose:** Detect patterns in sentiment including volatility, shifts, and consistency measures
**Returns:** Dictionary containing volatility, sentiment_shifts, shift_rate, consistency, predominant_sentiment

### `generate_sentiment_summary(analysis_results)`
**Purpose:** Generate human-readable summary of sentiment analysis results
**Returns:** String summary of overall sentiment patterns and key findings

## Survey Analysis (`survey_analysis.py`)

### `analyze_response_quality(responses)`
**Purpose:** Analyze quality and completeness of survey responses including categorization by response type
**Returns:** Dictionary containing quality_metrics (response rates, lengths, categories) and response_categories

### `analyze_survey_by_questions(survey_data)`
**Purpose:** Analyze survey responses grouped by individual questions with quality, sentiment, and content analysis
**Returns:** Dictionary containing per-question analysis with response counts, quality metrics, sentiment summary, themes, keywords

### `compare_questions(survey_data)`
**Purpose:** Compare responses across different survey questions to identify patterns and contrasts
**Returns:** Dictionary containing question_statistics, question_comparisons, summary with most positive/negative questions

### `analyze_respondent_patterns(survey_data, respondent_metadata=None)`
**Purpose:** Analyze patterns across individual respondents including engagement levels and consistency
**Returns:** Dictionary containing respondent_analysis and summary_statistics with engagement patterns

### `generate_survey_report(survey_data, question_metadata=None)`
**Purpose:** Generate comprehensive human-readable survey analysis report
**Returns:** String report with survey overview, question analysis, cross-question insights, respondent patterns

### `analyze_survey_data(survey_data, question_metadata=None, respondent_metadata=None)`
**Purpose:** Comprehensive analysis combining all survey analysis methods
**Returns:** Dictionary containing question_analysis, question_comparison, respondent_analysis, summary_report

## Text Analysis (`text_analysis.py`)

### `preprocess_text(text)`
**Purpose:** Preprocess text for analysis by tokenizing, removing stopwords, and lemmatizing
**Returns:** List of preprocessed tokens

### `analyze_text_frequency(text)`
**Purpose:** Analyze word frequency distributions in text after preprocessing
**Returns:** Dictionary of word frequencies

### `analyze_text_similarity(text1, text2)`
**Purpose:** Calculate similarity between two texts using Jaccard similarity coefficient
**Returns:** Float similarity score between 0 and 1

### `extract_key_phrases(text, n=5)`
**Purpose:** Extract the most important key phrases (bigrams) from text based on frequency
**Returns:** List of key phrases

### `analyze_text_patterns(text)`
**Purpose:** Analyze structural patterns in text including sentence/word counts and lengths
**Returns:** Dictionary containing num_sentences, num_words, avg_word_length, avg_sentence_length, key_phrases

## Thematic Analysis (`thematic_analysis.py`)

### `extract_key_concepts(texts, top_n=20)`
**Purpose:** Extract key concepts from text collection using TF-IDF scoring
**Returns:** List of (concept, score) tuples representing most important terms

### `identify_themes_clustering(texts, n_themes=5)`
**Purpose:** Identify themes using K-means clustering approach with TF-IDF vectorization
**Returns:** Dictionary containing themes with keywords, representative_texts, text_count, coherence score

### `identify_themes_lda(texts, n_themes=5)`
**Purpose:** Identify themes using Latent Dirichlet Allocation (LDA) topic modeling
**Returns:** Dictionary containing themes with keywords, keyword_weights, document_topic_probabilities, perplexity

### `analyze_theme_evolution(texts, timestamps, n_themes=5)`
**Purpose:** Analyze how themes evolve over time by grouping texts into time periods
**Returns:** Dictionary containing theme_evolution across time periods with frequency analysis

### `extract_quotes_by_theme(texts, theme_keywords, max_quotes=5)`
**Purpose:** Extract representative quotes that best exemplify a specific theme
**Returns:** List of representative quotes ranked by theme relevance

### `analyze_theme_relationships(themes)`
**Purpose:** Analyze relationships and similarities between identified themes
**Returns:** Dictionary containing relationships, similarity_matrix showing theme interconnections

### `generate_theme_report(analysis_results)`
**Purpose:** Generate comprehensive human-readable thematic analysis report
**Returns:** String report with theme descriptions, keywords, and representative quotes

### `analyze_themes(texts, method='clustering', n_themes=5)`
**Purpose:** Convenient wrapper function to perform thematic analysis using specified method
**Returns:** Dictionary with comprehensive theme analysis results

---

# Available Inferential Analytics Functions

## Bayesian Inference (`bayesian_inference.py`)

### `bayesian_t_test(data1, data2, prior_mean=0, prior_variance=1, credible_level=0.95)`
**Purpose:** Perform Bayesian t-test using conjugate priors with Bayes factors and credible intervals
**Returns:** Dictionary containing posterior distribution, bayes_factor, probability_direction, credible_interval, interpretation

### `bayesian_proportion_test(successes1, n1, successes2, n2, prior_alpha=1, prior_beta=1, credible_level=0.95)`
**Purpose:** Bayesian test for difference in proportions using Beta-Binomial conjugate analysis
**Returns:** Dictionary containing posterior_proportions, credible_interval_difference, probability_p1_greater, bayes_factor

### `calculate_bayes_factor(data, null_value=0, alternative='two-sided', prior_scale=1)`
**Purpose:** Calculate JZS Bayes factor for one-sample test with Cauchy prior on effect size
**Returns:** Dictionary containing bayes_factor_10, bayes_factor_01, log_bf_10, interpretation

### `calculate_posterior_distribution(data, prior_mean=0, prior_sd=10, likelihood='normal')`
**Purpose:** Calculate posterior distribution parameters using conjugate priors
**Returns:** Dictionary containing posterior mean/sd, prior parameters, shrinkage_factor

### `calculate_credible_interval(posterior_samples, credible_level=0.95, method='hdi')`
**Purpose:** Calculate credible intervals from posterior samples using HDI or equal-tailed methods
**Returns:** Dictionary containing interval bounds, point_estimates (mean, median, mode), contains_zero

### `bayesian_ab_test(control_successes, control_n, treatment_successes, treatment_n, prior_alpha=1, prior_beta=1, n_simulations=10000)`
**Purpose:** Bayesian A/B test for conversion rates with risk metrics and expected uplift
**Returns:** Dictionary containing probability_treatment_better, expected_relative_uplift, risk_metrics, recommendation

## Bootstrap Methods (`bootstrap_methods.py`)

### `bootstrap_mean(data, n_bootstrap=10000, confidence=0.95, method='percentile')`
**Purpose:** Bootstrap confidence interval for mean using percentile, BCa, or basic methods
**Returns:** Dictionary containing confidence_interval, bootstrap_distribution statistics, bias estimation

### `bootstrap_median(data, n_bootstrap=10000, confidence=0.95)`
**Purpose:** Bootstrap confidence interval for median with robust non-parametric estimation
**Returns:** Dictionary containing confidence_interval, bootstrap_distribution of medians

### `bootstrap_correlation(data, var1, var2, n_bootstrap=10000, confidence=0.95, method='pearson')`
**Purpose:** Bootstrap confidence intervals for correlation coefficients (Pearson, Spearman)
**Returns:** Dictionary containing confidence_interval, bootstrap_distribution statistics

### `bootstrap_regression(data, dependent_var, independent_vars, n_bootstrap=1000, confidence=0.95)`
**Purpose:** Bootstrap confidence intervals for regression coefficients and model parameters
**Returns:** Dictionary containing coefficient confidence_intervals, standard_errors, significance tests

### `bootstrap_std(data, n_bootstrap=10000, confidence=0.95, method='percentile')`
**Purpose:** Bootstrap confidence interval for standard deviation with bias correction
**Returns:** Dictionary containing confidence_interval, bootstrap_distribution, bias estimation

### `bootstrap_quantile(data, quantile=0.5, n_bootstrap=10000, confidence=0.95)`
**Purpose:** Bootstrap confidence interval for any quantile (percentile) of the distribution
**Returns:** Dictionary containing confidence_interval for specified quantile

### `bootstrap_difference_means(data1, data2, n_bootstrap=10000, confidence=0.95)`
**Purpose:** Bootstrap confidence interval for difference between two means with effect size
**Returns:** Dictionary containing confidence_interval, effect_size (Cohen's d), interpretation

### `bootstrap_ratio_means(data1, data2, n_bootstrap=10000, confidence=0.95)`
**Purpose:** Bootstrap confidence interval for ratio of two means with outlier handling
**Returns:** Dictionary containing confidence_interval, interpretation of ratio significance

### `permutation_test(data1, data2, statistic='mean_diff', n_permutations=10000, alternative='two-sided')`
**Purpose:** Non-parametric permutation test for comparing two samples under null hypothesis
**Returns:** Dictionary containing p_value, permutation_distribution, effect_size, interpretation

### `jackknife_estimate(data, statistic_func, confidence=0.95)`
**Purpose:** Jackknife estimation for bias and variance of any statistic with bias correction
**Returns:** Dictionary containing bias, bias_corrected_estimate, standard_error, confidence_interval

### `bootstrap_hypothesis_test(data1, data2, null_hypothesis='equal_means', n_bootstrap=10000, alternative='two-sided')`
**Purpose:** Bootstrap-based hypothesis testing with null hypothesis simulation
**Returns:** Dictionary containing p_value, confidence_interval, bootstrap_null_distribution

## Confidence Intervals (`confidence_intervals.py`)

### `calculate_mean_ci(data, confidence=0.95, method='t')`
**Purpose:** Calculate confidence interval for mean using t-distribution or normal approximation
**Returns:** Dictionary containing confidence_interval, standard_error, margin_of_error, degrees_of_freedom

### `calculate_proportion_ci(successes, n, confidence=0.95, method='wilson')`
**Purpose:** Calculate confidence intervals for proportions using Wilson, Wald, or exact methods
**Returns:** Dictionary containing confidence_interval, standard_error, method-specific parameters

### `calculate_difference_ci(data1, data2, confidence=0.95, paired=False)`
**Purpose:** Calculate confidence interval for difference between means (paired or independent)
**Returns:** Dictionary containing confidence_interval for mean difference, standard_error, degrees_of_freedom

### `calculate_correlation_ci(r, n, confidence=0.95, method='pearson')`
**Purpose:** Calculate confidence interval for correlation using Fisher's z-transformation
**Returns:** Dictionary containing confidence_interval transformed back to correlation scale

### `calculate_median_ci(data, confidence=0.95, method='exact')`
**Purpose:** Calculate confidence interval for median using exact binomial or bootstrap methods
**Returns:** Dictionary containing confidence_interval with exact or approximate bounds

### `calculate_bootstrap_ci(data, statistic_func, confidence=0.95, n_bootstrap=10000, method='percentile')`
**Purpose:** Generic bootstrap confidence interval for any user-defined statistic
**Returns:** Dictionary containing confidence_interval, bootstrap_mean, bootstrap_std

### `calculate_prediction_interval(model_predictions, residuals, new_x=None, confidence=0.95)`
**Purpose:** Calculate prediction intervals for regression models accounting for prediction uncertainty
**Returns:** Dictionary containing prediction_intervals, standard_error, degrees_of_freedom

### `calculate_odds_ratio_ci(table, confidence=0.95, method='woolf')`
**Purpose:** Calculate confidence interval for odds ratio from 2x2 contingency table
**Returns:** Dictionary containing confidence_interval, log_odds_ratio, standard_error_log_or

## Effect Sizes (`effect_sizes.py`)

### `calculate_cohens_d(group1, group2, pooled=True)`
**Purpose:** Calculate Cohen's d standardized effect size for mean differences
**Returns:** Dictionary containing cohens_d, confidence_interval, interpretation, pooled_sd, sample_sizes

### `calculate_hedges_g(group1, group2)`
**Purpose:** Calculate Hedges' g (bias-corrected Cohen's d) for small sample sizes
**Returns:** Dictionary containing hedges_g, confidence_interval, cohens_d, correction_factor

### `calculate_glass_delta(treatment, control)`
**Purpose:** Calculate Glass's delta using control group standard deviation
**Returns:** Dictionary containing glass_delta, interpretation, mean_difference, control_sd

### `calculate_eta_squared(data, group_column, value_column)`
**Purpose:** Calculate eta squared effect size for ANOVA (proportion of variance explained)
**Returns:** Dictionary containing eta_squared, cohens_f, interpretation, variance_explained

### `calculate_omega_squared(data, group_column, value_column)`
**Purpose:** Calculate omega squared (less biased than eta squared) for ANOVA
**Returns:** Dictionary containing omega_squared, interpretation, eta_squared, bias_reduction

### `calculate_cohens_f(eta_squared=None, groups_means=None, grand_mean=None, pooled_sd=None)`
**Purpose:** Calculate Cohen's f effect size for ANOVA from eta squared or group means
**Returns:** Dictionary containing cohens_f, interpretation, f_squared

### `calculate_cramers_v(contingency_table)`
**Purpose:** Calculate Cramér's V effect size for contingency tables with bias correction
**Returns:** Dictionary containing cramers_v, cramers_v_corrected, interpretation, chi_square

### `calculate_odds_ratio(table, confidence=0.95)`
**Purpose:** Calculate odds ratio for 2x2 table with confidence interval and interpretation
**Returns:** Dictionary containing odds_ratio, log_odds_ratio, confidence_interval, interpretation, significance

### `calculate_risk_ratio(table, confidence=0.95)`
**Purpose:** Calculate risk ratio (relative risk) for 2x2 table with confidence intervals
**Returns:** Dictionary containing risk_ratio, risk_exposed, risk_unexposed, confidence_interval, interpretation

### `calculate_nnt(risk_control, risk_treatment, confidence=0.95)`
**Purpose:** Calculate Number Needed to Treat from risk estimates
**Returns:** Dictionary containing nnt, absolute_risk_reduction, relative_risk_reduction, interpretation

## Hypothesis Testing (`hypothesis_testing.py`)

### `perform_t_test(data1, data2, alternative='two-sided', equal_var=True, alpha=0.05)`
**Purpose:** Comprehensive independent samples t-test with assumption testing and effect sizes
**Returns:** Dictionary containing t_statistic, p_value, effect_size, confidence_interval, assumptions, interpretation

### `perform_paired_t_test(data1, data2, alternative='two-sided', alpha=0.05)`
**Purpose:** Paired samples t-test for within-subjects comparisons with normality checking
**Returns:** Dictionary containing t_statistic, p_value, mean_difference, effect_size, normality_test

### `perform_welch_t_test(data1, data2, alternative='two-sided', alpha=0.05)`
**Purpose:** Welch's t-test for unequal variances (wrapper for t-test with equal_var=False)
**Returns:** Dictionary with Welch-adjusted degrees of freedom and test statistics

### `perform_anova(data, group_column, value_column, alpha=0.05, post_hoc=True)`
**Purpose:** One-way ANOVA with assumption testing and optional post-hoc comparisons
**Returns:** Dictionary containing f_statistic, p_value, effect_sizes, group_statistics, assumptions, post_hoc

### `perform_two_way_anova(data, factor1_column, factor2_column, value_column, interaction=True, alpha=0.05)`
**Purpose:** Two-way ANOVA with interaction terms and factor analysis
**Returns:** Dictionary containing main effects, interaction effects, cell_statistics, r_squared

### `perform_repeated_measures_anova(data, subject_column, within_column, value_column, between_column=None, alpha=0.05)`
**Purpose:** Repeated measures and mixed ANOVA with sphericity testing
**Returns:** Dictionary containing within/between effects, sphericity_test, partial_eta_squared

### `perform_chi_square_test(observed, expected=None, alpha=0.05, correction=True)`
**Purpose:** Chi-square test of independence or goodness of fit with effect sizes
**Returns:** Dictionary containing chi2_statistic, p_value, effect_size (Cramér's V), expected_frequencies, residuals

### `perform_fisher_exact_test(table, alternative='two-sided', alpha=0.05)`
**Purpose:** Fisher's exact test for 2x2 contingency tables with odds ratio confidence intervals
**Returns:** Dictionary containing p_value, odds_ratio, odds_ratio_ci, interpretation

### `perform_mcnemar_test(table, correction=True, alpha=0.05)`
**Purpose:** McNemar's test for paired categorical data with exact or chi-square approximation
**Returns:** Dictionary containing chi2_statistic, p_value, discordant_pairs, method used

### `perform_correlation_test(data, x_column, y_column, method="pearson", alpha=0.05)`
**Purpose:** Correlation test with assumption checking and confidence intervals
**Returns:** Dictionary containing correlation, p_value, confidence_interval, r_squared, interpretation, assumptions

### `perform_partial_correlation(data, x_column, y_column, control_columns, method="pearson", alpha=0.05)`
**Purpose:** Partial correlation controlling for covariates using pingouin
**Returns:** Dictionary containing partial correlation, p_value, controlled_variables, confidence_interval

### `hypothesis_test_summary(data, test_type, **kwargs)`
**Purpose:** Automated hypothesis test selection and execution with recommendations
**Returns:** Dictionary containing test results and statistical recommendations

## Inference Utilities (`inference_utils.py`)

### `validate_series_data(data, min_observations=2, name="data")`
**Purpose:** Validate and clean pandas Series for statistical analysis with missing data assessment
**Returns:** Dictionary containing validation status, clean_data, missing statistics

### `validate_two_samples(data1, data2, min_observations=2, names=("data1", "data2"))`
**Purpose:** Validate two samples for comparative statistical analysis
**Returns:** Dictionary containing validation for both samples and total sample size

### `validate_dataframe_columns(data, required_columns, min_observations=2)`
**Purpose:** Validate DataFrame has required columns with sufficient complete observations
**Returns:** Dictionary containing validation status, clean_data, missing_percentage

### `test_normality(data, alpha=0.05, test='shapiro')`
**Purpose:** Test normality assumption using Shapiro-Wilk, Anderson-Darling, or Kolmogorov-Smirnov
**Returns:** Dictionary containing test_statistic, p_value, assumption_met, test interpretation

### `test_equal_variances(data1, data2, alpha=0.05, test='levene')`
**Purpose:** Test equal variances assumption using Levene's, Bartlett's, or Fligner-Killeen tests
**Returns:** Dictionary containing test_statistic, p_value, equal_variances, assumption_met

### `test_independence(data, alpha=0.05)`
**Purpose:** Test independence assumption using runs test for randomness
**Returns:** Dictionary containing runs statistics, z_statistic, p_value, independent

### `calculate_standard_error(data, statistic='mean')`
**Purpose:** Calculate standard error for various statistics (mean, proportion, median)
**Returns:** Float value of standard error

### `check_test_assumptions(data1, data2=None, test_type='two_sample_t', alpha=0.05)`
**Purpose:** Comprehensive assumption checking for statistical tests with recommendations
**Returns:** Dictionary containing all assumption tests, overall assessment, test recommendations

## Multiple Comparisons (`multiple_comparisons.py`)

### `bonferroni_correction(p_values, alpha=0.05)`
**Purpose:** Apply Bonferroni correction for multiple testing with family-wise error rate control
**Returns:** Dictionary containing corrected_alpha, adjusted_p_values, reject_null, n_significant

### `holm_bonferroni_correction(p_values, alpha=0.05)`
**Purpose:** Apply Holm-Bonferroni step-down procedure (less conservative than Bonferroni)
**Returns:** Dictionary containing step-wise adjusted p-values, rejection decisions

### `benjamini_hochberg_correction(p_values, alpha=0.05)`
**Purpose:** Apply Benjamini-Hochberg FDR correction for controlling false discovery rate
**Returns:** Dictionary containing adjusted_p_values, false_discovery_rate, expected_false_discoveries

### `benjamini_yekutieli_correction(p_values, alpha=0.05)`
**Purpose:** Apply Benjamini-Yekutieli FDR correction for dependent tests (more conservative)
**Returns:** Dictionary containing adjusted_p_values suitable for dependent multiple tests

### `tukey_hsd_test(data, group_column, value_column, alpha=0.05)`
**Purpose:** Tukey's HSD test for all pairwise comparisons after ANOVA
**Returns:** Dictionary containing pairwise comparisons, confidence_intervals, group_statistics

### `dunnett_test(data, group_column, value_column, control_group, alpha=0.05)`
**Purpose:** Dunnett's test for comparing all treatment groups to a single control
**Returns:** Dictionary containing comparisons vs control, adjusted_p_values, control_stats

### `games_howell_test(data, group_column, value_column, alpha=0.05)`
**Purpose:** Games-Howell test for pairwise comparisons with unequal variances
**Returns:** Dictionary containing pairwise comparisons with Welch-corrected statistics

### `apply_multiple_corrections(p_values, alpha=0.05, methods=None)`
**Purpose:** Apply multiple correction methods simultaneously for comparison
**Returns:** Dictionary containing results from all specified correction methods with summary

## Nonparametric Tests (`nonparametric_tests.py`)

### `mann_whitney_u_test(data1, data2, alternative='two-sided', use_continuity=True, alpha=0.05)`
**Purpose:** Mann-Whitney U test (Wilcoxon rank-sum) for comparing two independent samples
**Returns:** Dictionary containing U_statistic, p_value, effect_size (rank biserial r), Hodges-Lehmann estimate

### `wilcoxon_signed_rank_test(data1, data2, alternative='two-sided', mode='auto', alpha=0.05)`
**Purpose:** Wilcoxon signed-rank test for paired samples with pseudomedian estimation
**Returns:** Dictionary containing test_statistic, p_value, effect_size, pseudomedian, interpretation

### `kruskal_wallis_test(data, group_column, value_column, alpha=0.05, post_hoc=True)`
**Purpose:** Kruskal-Wallis H test for multiple independent groups with optional post-hoc tests
**Returns:** Dictionary containing h_statistic, p_value, effect_size (epsilon squared), group_statistics, post_hoc

### `friedman_test(data, value_columns, alpha=0.05)`
**Purpose:** Friedman test for repeated measures with multiple conditions
**Returns:** Dictionary containing chi2_statistic, p_value, effect_size (Kendall's W), mean_ranks, post_hoc

### `runs_test(data, cutoff=None, alpha=0.05)`
**Purpose:** Runs test for randomness in sequence data with normal approximation
**Returns:** Dictionary containing n_runs, expected_runs, z_statistic, p_value, interpretation

### `kolmogorov_smirnov_test(data1, data2='norm', args=(), alpha=0.05)`
**Purpose:** Kolmogorov-Smirnov test for distribution comparison (one or two sample)
**Returns:** Dictionary containing d_statistic, p_value, test_type, interpretation

### `anderson_darling_test(data, dist='norm')`
**Purpose:** Anderson-Darling test for goodness of fit with multiple significance levels
**Returns:** Dictionary containing statistic, critical_values, significance_levels, interpretations

### `shapiro_wilk_test(data, alpha=0.05)`
**Purpose:** Shapiro-Wilk test for normality with sample size warnings
**Returns:** Dictionary containing w_statistic, p_value, interpretation, recommendation

### `mood_median_test(*samples, alpha=0.05)`
**Purpose:** Mood's median test for comparing medians across multiple groups
**Returns:** Dictionary containing chi2_statistic, p_value, grand_median, sample_medians, effect_size

## Power Analysis (`power_analysis.py`)

### `calculate_sample_size_t_test(effect_size, alpha=0.05, power=0.80, test_type='two-sample', alternative='two-sided', ratio=1.0)`
**Purpose:** Calculate required sample size for t-tests given effect size and desired power
**Returns:** Dictionary containing sample sizes, effect_size_interpretation, recommendation

### `calculate_sample_size_anova(effect_size, n_groups, alpha=0.05, power=0.80)`
**Purpose:** Calculate sample size for one-way ANOVA with Cohen's f effect size
**Returns:** Dictionary containing n_per_group, total_sample_size, degrees_of_freedom, recommendation

### `calculate_sample_size_proportion(p1, p2, alpha=0.05, power=0.80, alternative='two-sided', ratio=1.0)`
**Purpose:** Calculate sample size for comparing two proportions with effect size calculations
**Returns:** Dictionary containing sample sizes, effect_size_h, absolute_difference, relative_risk, odds_ratio

### `calculate_sample_size_correlation(r, alpha=0.05, power=0.80, alternative='two-sided')`
**Purpose:** Calculate sample size for correlation test using Fisher's z transformation
**Returns:** Dictionary containing sample_size, correlation_interpretation, minimum_detectable_r

### `calculate_power_t_test(n, effect_size, alpha=0.05, test_type='two-sample', alternative='two-sided')`
**Purpose:** Calculate statistical power for t-tests given sample size and effect size
**Returns:** Dictionary containing power, type_ii_error, interpretation

### `calculate_power_anova(n_per_group, effect_size, n_groups, alpha=0.05)`
**Purpose:** Calculate statistical power for ANOVA given sample sizes and effect size
**Returns:** Dictionary containing power, interpretation, minimum_detectable_effect

### `calculate_effect_size_needed(n, alpha=0.05, power=0.80, test_type='two-sample')`
**Purpose:** Calculate minimum detectable effect size given sample size and desired power
**Returns:** Dictionary containing minimum_effect_size, effect_size_interpretation, practical_significance

### `post_hoc_power_analysis(observed_effect, n, alpha=0.05, test_type='two-sample')`
**Purpose:** Perform post-hoc power analysis on completed studies with sample size recommendations
**Returns:** Dictionary containing achieved_power, sufficient_power, sample_size_for_80_power, recommendation

## Regression Analysis (`regression_analysis.py`)

### `perform_linear_regression(data, dependent_var, independent_vars, include_intercept=True, alpha=0.05)`
**Purpose:** Comprehensive linear regression with diagnostics, confidence intervals, and assumption testing
**Returns:** Dictionary containing coefficients, r_squared, f_statistic, confidence_intervals, diagnostics

### `perform_multiple_regression(data, dependent_var, independent_vars, interaction_terms=None, polynomial_terms=None, alpha=0.05)`
**Purpose:** Multiple regression with interaction terms, polynomial features, and multicollinearity assessment
**Returns:** Dictionary containing model results, VIF values, best_model_vars from stepwise selection

### `perform_logistic_regression(data, dependent_var, independent_vars, alpha=0.05)`
**Purpose:** Logistic regression for binary outcomes with odds ratios and classification metrics
**Returns:** Dictionary containing coefficients with odds_ratios, mcfadden_r2, classification_metrics, confusion_matrix

### `perform_poisson_regression(data, dependent_var, independent_vars, exposure=None, alpha=0.05)`
**Purpose:** Poisson regression for count data with overdispersion testing and rate ratios
**Returns:** Dictionary containing coefficients with rate_ratios, deviance, overdispersion assessment

### `calculate_regression_diagnostics(model, X, y)`
**Purpose:** Comprehensive regression diagnostics including residuals, influential observations, assumptions
**Returns:** Dictionary containing normality tests, heteroscedasticity tests, autocorrelation, leverage, Cook's distance

### `calculate_vif(X)`
**Purpose:** Calculate Variance Inflation Factors for multicollinearity assessment
**Returns:** Dictionary containing VIF values, high_multicollinearity variables, interpretation

### `perform_ridge_regression(data, dependent_var, independent_vars, alpha_values=None, cv_folds=5)`
**Purpose:** Ridge regression with cross-validation for regularization parameter selection
**Returns:** Dictionary containing best_alpha, coefficients (standardized and unstandardized), cv_results

### `perform_lasso_regression(data, dependent_var, independent_vars, alpha_values=None, cv_folds=5)`
**Purpose:** Lasso regression for feature selection with cross-validation and sparsity
**Returns:** Dictionary containing selected_features, coefficients, best_alpha, feature selection results

### `perform_robust_regression(data, dependent_var, independent_vars, method='huber')`
**Purpose:** Robust regression resistant to outliers using Huber or Tukey methods
**Returns:** Dictionary containing robust coefficients, influential_observations, comparison_with_ols

## Time Series Inference (`time_series_inference.py`)

### `test_stationarity(series, test_types=['adf', 'kpss'], alpha=0.05)`
**Purpose:** Test time series stationarity using ADF and KPSS tests with overall assessment
**Returns:** Dictionary containing test statistics, p_values, critical_values, overall_assessment

### `test_autocorrelation(series, lags=40, alpha=0.05)`
**Purpose:** Test for autocorrelation using ACF, PACF, and Ljung-Box test with significant lags
**Returns:** Dictionary containing acf, pacf values, confidence_intervals, ljung_box results, interpretation

### `test_seasonality(series, period, test_type='decomposition', alpha=0.05)`
**Purpose:** Test for seasonality using seasonal decomposition with strength measures
**Returns:** Dictionary containing seasonal_strength, f_statistic, p_value, seasonal_component analysis

### `granger_causality_test(data, cause_var, effect_var, max_lag=10, alpha=0.05)`
**Purpose:** Granger causality test for temporal precedence relationships between variables
**Returns:** Dictionary containing lag_tests, best_lag, stationarity_check, conclusion

### `cointegration_test(series1, series2, trend='c', alpha=0.05)`
**Purpose:** Engle-Granger cointegration test for long-run relationships between non-stationary series
**Returns:** Dictionary containing test_statistic, p_value, critical_values, cointegrated, interpretation

### `change_point_detection(series, method='cusum', threshold=0.05)`
**Purpose:** Detect structural breaks in time series using CUSUM or other methods
**Returns:** Dictionary containing cusum_values, change_points, n_change_points, threshold

### `forecast_accuracy_tests(actual, forecast, alpha=0.05)`
**Purpose:** Test forecast accuracy with bias testing, autocorrelation checks, and accuracy metrics
**Returns:** Dictionary containing accuracy_metrics (MAE, MSE, RMSE, MAPE), bias_test, error_autocorrelation

## Function Categories Summary

**Descriptive Analytics:**
- **Basic Statistics (6 functions):** Core descriptive statistics, correlations, grouped analysis
- **Categorical Analysis (6 functions):** Frequency analysis, association tests, cross-tabulation
- **Distribution Analysis (4 functions):** Distribution fitting, normality testing, shape analysis
- **Geospatial Analysis (3 functions):** Spatial patterns, clustering, autocorrelation
- **Temporal Analysis (3 functions):** Time patterns, seasonality, trend analysis

**Qualitative Analytics:**
- **Content Analysis (6 functions):** Text structure, categories, linguistic features, patterns
- **Qualitative Statistics (4 functions):** Text statistics, quality metrics, comprehensive summaries
- **Sentiment Analysis (7 functions):** Sentiment scoring, emotion detection, trend analysis
- **Survey Analysis (6 functions):** Response quality, question comparison, respondent patterns
- **Text Analysis (5 functions):** Text preprocessing, frequency, similarity, key phrases
- **Thematic Analysis (8 functions):** Theme identification, concept extraction, evolution analysis

**Inferential Analytics:**
- **Bayesian Inference (6 functions):** Bayesian testing, posterior distributions, Bayes factors
- **Bootstrap Methods (11 functions):** Bootstrap CIs, permutation tests, resampling methods
- **Confidence Intervals (8 functions):** Parametric and non-parametric confidence intervals
- **Effect Sizes (10 functions):** Standardized effect sizes, practical significance measures
- **Hypothesis Testing (12 functions):** Parametric tests, ANOVA, correlation, chi-square tests
- **Inference Utilities (8 functions):** Data validation, assumption testing, diagnostic tools
- **Multiple Comparisons (8 functions):** Multiple testing corrections, post-hoc tests
- **Nonparametric Tests (9 functions):** Distribution-free tests, rank-based methods
- **Power Analysis (8 functions):** Sample size planning, power calculations, effect size estimation
- **Regression Analysis (9 functions):** Linear, logistic, robust regression with diagnostics
- **Time Series Inference (7 functions):** Stationarity, causality, seasonality, forecasting tests

**Total: 147 individual analytics functions available**
- **Descriptive: 22 functions**
- **Qualitative: 36 functions**
- **Inferential: 89 functions**
