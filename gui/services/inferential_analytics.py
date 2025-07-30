"""
Inferential Analytics Handler
Specialized service for inferential statistics and hypothesis testing
"""

from typing import Dict, List, Any, Optional, Union
import threading
import urllib.parse
from kivy.clock import Clock
from utils.cross_platform_toast import toast


class InferentialAnalyticsHandler:
    """Handler for inferential analytics operations - Business Logic Only"""
    
    def __init__(self, analytics_service, screen):
        self.analytics_service = analytics_service
        self.screen = screen
        self.selected_variables = []
        self.selected_groups = []
    
    # CORRELATION ANALYSIS
    def run_correlation_analysis(self, project_id: str, config: Dict = None):
        """Run correlation analysis for the project"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_correlation_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_correlation_thread(self, project_id: str, config: Dict):
        """Background thread for correlation analysis"""
        try:
            variables = config.get('variables', []) if config else []
            method = config.get('method', 'pearson') if config else 'pearson'
            significance_level = config.get('significance_level', 0.05) if config else 0.05
            
            results = self.analytics_service.run_correlation_analysis(
                project_id, variables, method, significance_level
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_correlation_results(results), 0
            )
        except Exception as e:
            print(f"Error in correlation analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Correlation analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_correlation_results(self, results):
        """Handle correlation analysis results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.correlation_results = results
        self.screen.current_analysis_type = "correlation"
        toast("Correlation analysis completed successfully")
    
    # T-TEST ANALYSIS
    def run_t_test(self, project_id: str, config: Dict = None):
        """Run t-test analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_t_test_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_t_test_thread(self, project_id: str, config: Dict):
        """Background thread for t-test analysis"""
        try:
            dependent_var = config.get('dependent_variable') if config else None
            independent_var = config.get('independent_variable') if config else None
            test_type = config.get('test_type', 'two_sample') if config else 'two_sample'
            alternative = config.get('alternative', 'two_sided') if config else 'two_sided'
            confidence_level = config.get('confidence_level', 0.95) if config else 0.95
            
            results = self.analytics_service.run_t_test(
                project_id, dependent_var, independent_var, test_type, alternative, confidence_level
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_t_test_results(results), 0
            )
        except Exception as e:
            print(f"Error in t-test analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("T-test analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_t_test_results(self, results):
        """Handle t-test analysis results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.t_test_results = results
        self.screen.current_analysis_type = "t_test"
        toast("T-test analysis completed successfully")
    
    # ANOVA ANALYSIS
    def run_anova(self, project_id: str, config: Dict = None):
        """Run ANOVA analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_anova_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_anova_thread(self, project_id: str, config: Dict):
        """Background thread for ANOVA analysis"""
        try:
            dependent_var = config.get('dependent_variable') if config else None
            independent_vars = config.get('independent_variables', []) if config else []
            anova_type = config.get('anova_type', 'one_way') if config else 'one_way'
            post_hoc = config.get('post_hoc', True) if config else True
            post_hoc_method = config.get('post_hoc_method', 'tukey') if config else 'tukey'
            
            results = self.analytics_service.run_anova(
                project_id, dependent_var, independent_vars, anova_type, post_hoc, post_hoc_method
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_anova_results(results), 0
            )
        except Exception as e:
            print(f"Error in ANOVA analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("ANOVA analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_anova_results(self, results):
        """Handle ANOVA analysis results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.anova_results = results
        self.screen.current_analysis_type = "anova"
        toast("ANOVA analysis completed successfully")
    
    # REGRESSION ANALYSIS
    def run_regression(self, project_id: str, config: Dict = None):
        """Run regression analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_regression_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_regression_thread(self, project_id: str, config: Dict):
        """Background thread for regression analysis"""
        try:
            dependent_var = config.get('dependent_variable') if config else None
            independent_vars = config.get('independent_variables', []) if config else []
            regression_type = config.get('regression_type', 'linear') if config else 'linear'
            include_diagnostics = config.get('include_diagnostics', True) if config else True
            confidence_level = config.get('confidence_level', 0.95) if config else 0.95
            
            results = self.analytics_service.run_regression_analysis(
                project_id, dependent_var, independent_vars, regression_type, include_diagnostics, confidence_level
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_regression_results(results), 0
            )
        except Exception as e:
            print(f"Error in regression analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Regression analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_regression_results(self, results):
        """Handle regression analysis results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.regression_results = results
        self.screen.current_analysis_type = "regression"
        toast("Regression analysis completed successfully")
    
    # CHI-SQUARE TEST
    def run_chi_square_test(self, project_id: str, config: Dict = None):
        """Run chi-square test"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_chi_square_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_chi_square_thread(self, project_id: str, config: Dict):
        """Background thread for chi-square test"""
        try:
            variable1 = config.get('variable1') if config else None
            variable2 = config.get('variable2') if config else None
            test_type = config.get('test_type', 'independence') if config else 'independence'
            expected_frequencies = config.get('expected_frequencies') if config else None
            
            results = self.analytics_service.run_chi_square_test(
                project_id, variable1, variable2, test_type, expected_frequencies
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_chi_square_results(results), 0
            )
        except Exception as e:
            print(f"Error in chi-square test: {e}")
            Clock.schedule_once(
                lambda dt: toast("Chi-square test failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_chi_square_results(self, results):
        """Handle chi-square test results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.chi_square_results = results
        self.screen.current_analysis_type = "chi_square"
        toast("Chi-square test completed successfully")
    
    # NONPARAMETRIC TESTS
    def run_nonparametric_test(self, project_id: str, config: Dict = None):
        """Run nonparametric test"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_nonparametric_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_nonparametric_thread(self, project_id: str, config: Dict):
        """Background thread for nonparametric test"""
        try:
            test_type = config.get('test_type', 'mann_whitney') if config else 'mann_whitney'
            variables = config.get('variables', []) if config else []
            groups = config.get('groups') if config else None
            alternative = config.get('alternative', 'two_sided') if config else 'two_sided'
            
            results = self.analytics_service.run_nonparametric_test(
                project_id, test_type, variables, groups, alternative
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_nonparametric_results(results), 0
            )
        except Exception as e:
            print(f"Error in nonparametric test: {e}")
            Clock.schedule_once(
                lambda dt: toast("Nonparametric test failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_nonparametric_results(self, results):
        """Handle nonparametric test results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.nonparametric_results = results
        self.screen.current_analysis_type = "nonparametric"
        toast("Nonparametric test completed successfully")
    
    # BAYESIAN ANALYSIS
    def run_bayesian_t_test(self, project_id: str, config: Dict = None):
        """Run Bayesian t-test"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_bayesian_t_test_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_bayesian_t_test_thread(self, project_id: str, config: Dict):
        """Background thread for Bayesian t-test"""
        try:
            variable1 = config.get('variable1') if config else None
            variable2 = config.get('variable2') if config else None
            prior_mean = config.get('prior_mean', 0) if config else 0
            prior_variance = config.get('prior_variance', 1) if config else 1
            credible_level = config.get('credible_level', 0.95) if config else 0.95
            
            results = self.analytics_service.run_bayesian_t_test(
                project_id, variable1, variable2, prior_mean, prior_variance, credible_level
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_bayesian_results(results), 0
            )
        except Exception as e:
            print(f"Error in Bayesian t-test: {e}")
            Clock.schedule_once(
                lambda dt: toast("Bayesian t-test failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_bayesian_results(self, results):
        """Handle Bayesian test results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.bayesian_results = results
        self.screen.current_analysis_type = "bayesian"
        toast("Bayesian analysis completed successfully")
    
    # EFFECT SIZE ANALYSIS
    def calculate_effect_size(self, project_id: str, config: Dict = None):
        """Calculate effect size"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._calculate_effect_size_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _calculate_effect_size_thread(self, project_id: str, config: Dict):
        """Background thread for effect size calculation"""
        try:
            dependent_var = config.get('dependent_variable') if config else None
            independent_var = config.get('independent_variable') if config else None
            effect_size_measure = config.get('effect_size_measure', 'cohen_d') if config else 'cohen_d'
            
            results = self.analytics_service.calculate_effect_size(
                project_id, dependent_var, independent_var, effect_size_measure
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_effect_size_results(results), 0
            )
        except Exception as e:
            print(f"Error in effect size calculation: {e}")
            Clock.schedule_once(
                lambda dt: toast("Effect size calculation failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_effect_size_results(self, results):
        """Handle effect size results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.effect_size_results = results
        self.screen.current_analysis_type = "effect_size"
        toast("Effect size calculation completed successfully")
    
    # POWER ANALYSIS
    def run_power_analysis(self, project_id: str, config: Dict = None):
        """Run power analysis"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_power_analysis_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_power_analysis_thread(self, project_id: str, config: Dict):
        """Background thread for power analysis"""
        try:
            test_type = config.get('test_type', 't_test') if config else 't_test'
            effect_size = config.get('effect_size') if config else None
            sample_size = config.get('sample_size') if config else None
            power = config.get('power') if config else None
            significance_level = config.get('significance_level', 0.05) if config else 0.05
            
            results = self.analytics_service.run_power_analysis(
                project_id, test_type, effect_size, sample_size, power, significance_level
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_power_analysis_results(results), 0
            )
        except Exception as e:
            print(f"Error in power analysis: {e}")
            Clock.schedule_once(
                lambda dt: toast("Power analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_power_analysis_results(self, results):
        """Handle power analysis results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.power_analysis_results = results
        self.screen.current_analysis_type = "power_analysis"
        toast("Power analysis completed successfully")
    
    # CONFIDENCE INTERVALS
    def calculate_confidence_intervals(self, project_id: str, config: Dict = None):
        """Calculate confidence intervals"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._calculate_confidence_intervals_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _calculate_confidence_intervals_thread(self, project_id: str, config: Dict):
        """Background thread for confidence intervals calculation"""
        try:
            variables = config.get('variables', []) if config else []
            confidence_level = config.get('confidence_level', 0.95) if config else 0.95
            interval_type = config.get('interval_type', 'mean') if config else 'mean'
            bootstrap_samples = config.get('bootstrap_samples', 1000) if config else 1000
            
            results = self.analytics_service.calculate_confidence_intervals(
                project_id, variables, confidence_level, interval_type, bootstrap_samples
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_confidence_intervals_results(results), 0
            )
        except Exception as e:
            print(f"Error in confidence intervals calculation: {e}")
            Clock.schedule_once(
                lambda dt: toast("Confidence intervals calculation failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_confidence_intervals_results(self, results):
        """Handle confidence intervals results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.confidence_intervals_results = results
        self.screen.current_analysis_type = "confidence_intervals"
        toast("Confidence intervals calculation completed successfully")
    
    # MULTIPLE COMPARISONS
    def run_multiple_comparisons(self, project_id: str, config: Dict = None):
        """Run multiple comparisons correction"""
        if not project_id:
            return
            
        self.screen.set_loading(True)
        threading.Thread(
            target=self._run_multiple_comparisons_thread,
            args=(project_id, config),
            daemon=True
        ).start()
    
    def _run_multiple_comparisons_thread(self, project_id: str, config: Dict):
        """Background thread for multiple comparisons"""
        try:
            p_values = config.get('p_values', []) if config else []
            alpha = config.get('alpha', 0.05) if config else 0.05
            methods = config.get('methods') if config else None
            
            results = self.analytics_service.run_multiple_comparisons_correction(
                project_id, p_values, alpha, methods
            )
            
            Clock.schedule_once(
                lambda dt: self._handle_multiple_comparisons_results(results), 0
            )
        except Exception as e:
            print(f"Error in multiple comparisons: {e}")
            Clock.schedule_once(
                lambda dt: toast("Multiple comparisons failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.screen.set_loading(False), 0
            )
    
    def _handle_multiple_comparisons_results(self, results):
        """Handle multiple comparisons results"""
        if 'error' in results:
            toast(f"Error: {results['error']}")
            return
            
        self.screen.multiple_comparisons_results = results
        self.screen.current_analysis_type = "multiple_comparisons"
        toast("Multiple comparisons completed successfully")
    
    # VARIABLE SELECTION HELPERS
    def update_selected_variables(self, variables: List[str]):
        """Update selected variables list"""
        self.selected_variables = variables
        self.screen.selected_variables = set(variables)
    
    def update_selected_groups(self, groups: List[str]):
        """Update selected groups list"""
        self.selected_groups = groups
        self.screen.selected_groups = set(groups)
    
    # ANALYSIS TYPE HELPERS
    def get_analysis_types(self):
        """Get available analysis types"""
        return [
            {'id': 'correlation', 'name': 'Correlation Analysis', 'icon': 'chart-line'},
            {'id': 't_test', 'name': 'T-Test', 'icon': 'test-tube'},
            {'id': 'anova', 'name': 'ANOVA', 'icon': 'chart-bar'},
            {'id': 'regression', 'name': 'Regression Analysis', 'icon': 'trending-up'},
            {'id': 'chi_square', 'name': 'Chi-Square Test', 'icon': 'grid'},
            {'id': 'nonparametric', 'name': 'Nonparametric Tests', 'icon': 'chart-scatter-plot'},
            {'id': 'bayesian', 'name': 'Bayesian Analysis', 'icon': 'brain'},
            {'id': 'effect_size', 'name': 'Effect Size', 'icon': 'arrow-expand'},
            {'id': 'power_analysis', 'name': 'Power Analysis', 'icon': 'flash'},
            {'id': 'confidence_intervals', 'name': 'Confidence Intervals', 'icon': 'target'},
            {'id': 'multiple_comparisons', 'name': 'Multiple Comparisons', 'icon': 'compare'}
        ]
    
    def get_test_options(self, analysis_type: str):
        """Get test options for specific analysis type"""
        options = {
            'correlation': ['pearson', 'spearman', 'kendall'],
            't_test': ['one_sample', 'two_sample', 'paired'],
            'anova': ['one_way', 'two_way', 'repeated_measures'],
            'regression': ['linear', 'multiple', 'logistic', 'poisson', 'ridge', 'lasso', 'robust'],
            'chi_square': ['independence', 'goodness_of_fit'],
            'nonparametric': ['mann_whitney', 'wilcoxon', 'kruskal_wallis', 'friedman', 'kolmogorov_smirnov', 'shapiro_wilk'],
            'bayesian': ['bayesian_t_test', 'bayesian_proportion_test', 'bayesian_ab_test'],
            'effect_size': ['cohen_d', 'hedges_g', 'glass_delta', 'eta_squared', 'omega_squared', 'cramers_v', 'odds_ratio'],
            'power_analysis': ['t_test', 'anova', 'correlation'],
            'confidence_intervals': ['mean', 'median', 'proportion', 'variance'],
            'multiple_comparisons': ['bonferroni', 'holm', 'benjamini_hochberg', 'benjamini_yekutieli']
        }
        return options.get(analysis_type, [])