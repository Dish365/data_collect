from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.window import Window

from utils.cross_platform_toast import toast
from kivymd.uix.menu import MDDropdownMenu

import json
import threading
import uuid
from typing import Dict, List, Any, Optional, Union

from widgets.loading_overlay import LoadingOverlay
from services.inferential_analytics import InferentialAnalyticsHandler

# KV file loaded by main app after theme initialization

class InferentialAnalyticsScreen(Screen):
    """Inferential Analytics Screen - handles UI interactions and delegates logic to service"""
    
    # Screen properties
    current_project_id = StringProperty(None, allownone=True)
    current_project_name = StringProperty("")
    project_list = ListProperty([])
    project_map = {}
    
    # Analysis state
    analysis_results = ObjectProperty({})
    is_loading = BooleanProperty(False)
    current_analysis_type = StringProperty("")
    
    # Data state
    project_variables = ListProperty([])
    selected_variables = ObjectProperty(set())
    selected_groups = ObjectProperty(set())
    analysis_options = ListProperty([])
    
    # Results state
    correlation_results = ObjectProperty({})
    t_test_results = ObjectProperty({})
    anova_results = ObjectProperty({})
    regression_results = ObjectProperty({})
    chi_square_results = ObjectProperty({})
    nonparametric_results = ObjectProperty({})
    bayesian_results = ObjectProperty({})
    effect_size_results = ObjectProperty({})
    power_analysis_results = ObjectProperty({})
    confidence_intervals_results = ObjectProperty({})
    multiple_comparisons_results = ObjectProperty({})
    
    # UI state
    selected_analysis_type = StringProperty("")
    selected_test_method = StringProperty("")
    significance_level = StringProperty("0.05")
    confidence_level = StringProperty("0.95")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.analytics_service = None
        self.handler = None
        self.analysis_menu = None
        self.test_method_menu = None
        self.variable_menus = {}
        
        # Available analysis types
        self.analysis_types = [
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
        
        # Test method options for each analysis type
        self.test_methods = {
            'correlation': ['pearson', 'spearman', 'kendall'],
            't_test': ['one_sample', 'two_sample', 'paired'],
            'anova': ['one_way', 'two_way', 'repeated_measures'],
            'regression': ['linear', 'multiple', 'logistic', 'poisson', 'ridge', 'lasso', 'robust'],
            'chi_square': ['independence', 'goodness_of_fit'],
            'nonparametric': ['mann_whitney', 'wilcoxon', 'kruskal_wallis', 'friedman', 'kolmogorov_smirnov', 'shapiro_wilk'],
            'bayesian': ['bayesian_t_test', 'bayesian_proportion_test'],
            'effect_size': ['cohen_d', 'hedges_g', 'glass_delta', 'eta_squared', 'omega_squared', 'cramers_v', 'odds_ratio'],
            'power_analysis': ['t_test', 'anova', 'correlation'],
            'confidence_intervals': ['mean', 'median', 'proportion', 'variance'],
            'multiple_comparisons': ['bonferroni', 'holm', 'benjamini_hochberg', 'benjamini_yekutieli']
        }
        
        Clock.schedule_once(self.init_screen, 0.1)
    
    def init_screen(self, dt):
        """Initialize screen components"""
        app = App.get_running_app()
        if hasattr(app, 'analytics_service'):
            self.analytics_service = app.analytics_service
            self.handler = InferentialAnalyticsHandler(self.analytics_service, self)
            
            # Load projects
            self.load_projects()
            
            # Setup analysis type menu
            self.setup_analysis_menu()
    
    def load_projects(self):
        """Load available projects"""
        try:
            # Use project service to get projects
            app = App.get_running_app()
            if hasattr(app, 'auth_service') and hasattr(app, 'db_service') and hasattr(app, 'sync_service'):
                from services.project_service import ProjectService
                project_service = ProjectService(app.auth_service, app.db_service, app.sync_service)
                projects, error = project_service.load_projects()
                if error:
                    print(f"Error loading projects: {error}")
                    return
            else:
                print("Error: Required services not available")
                return
            self.project_list = []
            self.project_map = {}
            
            for project in projects:
                project_item = {
                    'id': project['id'],
                    'name': project['name'],  # Fixed: use 'name' instead of 'title'
                    'description': project.get('description', ''),
                    'created_at': project.get('created_at', ''),
                    'responses_count': project.get('responses_count', 0)
                }
                self.project_list.append(project_item)
                self.project_map[project['id']] = project_item
                
        except Exception as e:
            print(f"Error loading projects: {e}")
            toast("Failed to load projects")
    
    def setup_analysis_menu(self):
        """Setup analysis type dropdown menu"""
        menu_items = []
        for analysis in self.analysis_types:
            menu_items.append({
                "text": analysis['name'],
                "viewclass": "MDListItem",
                "on_release": lambda x=analysis['id']: self.select_analysis_type(x),
            })
        
        self.analysis_menu = MDDropdownMenu(
            items=menu_items,
            width=dp(200),
        )
    
    def show_analysis_menu(self, caller):
        """Show analysis type menu"""
        if self.analysis_menu:
            self.analysis_menu.caller = caller
            self.analysis_menu.open()
    
    def select_analysis_type(self, analysis_type):
        """Select analysis type"""
        self.selected_analysis_type = analysis_type
        if self.analysis_menu:
            self.analysis_menu.dismiss()
        
        # Update analysis type button text
        analysis_name = next((a['name'] for a in self.analysis_types if a['id'] == analysis_type), analysis_type)
        if hasattr(self.ids, 'analysis_type_button'):
            self.ids.analysis_type_button.text = analysis_name
        
        # Setup test method menu for selected analysis type
        self.setup_test_method_menu(analysis_type)
        
        # Update UI based on selected analysis type
        self.update_analysis_ui(analysis_type)
    
    def setup_test_method_menu(self, analysis_type):
        """Setup test method dropdown menu"""
        methods = self.test_methods.get(analysis_type, [])
        if not methods:
            return
        
        menu_items = []
        for method in methods:
            menu_items.append({
                "text": method.replace('_', ' ').title(),
                "viewclass": "MDListItem",
                "on_release": lambda x=method: self.select_test_method(x),
            })
        
        self.test_method_menu = MDDropdownMenu(
            items=menu_items,
            width=dp(200),
        )
    
    def show_test_method_menu(self, caller):
        """Show test method menu"""
        if self.test_method_menu:
            self.test_method_menu.caller = caller
            self.test_method_menu.open()
    
    def select_test_method(self, method):
        """Select test method"""
        self.selected_test_method = method
        if self.test_method_menu:
            self.test_method_menu.dismiss()
        
        # Update test method button text
        if hasattr(self.ids, 'test_method_button'):
            self.ids.test_method_button.text = method.replace('_', ' ').title()
    
    def update_analysis_ui(self, analysis_type):
        """Update UI based on selected analysis type"""
        # Clear previous results
        self.analysis_results = {}
        self.current_analysis_type = ""
        
        # Update variable selection requirements
        self.update_variable_requirements(analysis_type)
        
        # Show/hide relevant UI components
        self.toggle_ui_components(analysis_type)
    
    def update_variable_requirements(self, analysis_type):
        """Update variable selection requirements based on analysis type"""
        # This will be handled by the KV file and updated dynamically
        pass
    
    def toggle_ui_components(self, analysis_type):
        """Show/hide UI components based on analysis type"""
        # This will be handled by the KV file and updated dynamically
        pass
    
    def select_project(self, project_id):
        """Select a project for analysis"""
        if project_id in self.project_map:
            self.current_project_id = project_id
            self.current_project_name = self.project_map[project_id]['name']
            
            # Load project variables
            self.load_project_variables(project_id)
            
            toast(f"Project '{self.current_project_name}' selected")
    
    def load_project_variables(self, project_id):
        """Load variables for the selected project"""
        try:
            variables = self.analytics_service.get_project_variables(project_id)
            self.project_variables = variables
        except Exception as e:
            print(f"Error loading project variables: {e}")
            toast("Failed to load project variables")
    
    def toggle_variable_selection(self, variable, selected):
        """Toggle variable selection"""
        if selected:
            self.selected_variables.add(variable)
        else:
            self.selected_variables.discard(variable)
        
        # Update selected variables in handler
        if self.handler:
            self.handler.update_selected_variables(list(self.selected_variables))
    
    def run_analysis(self):
        """Run the selected analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.selected_analysis_type:
            toast("Please select an analysis type")
            return
        
        # Prepare analysis configuration
        config = self.prepare_analysis_config()
        
        # Run analysis based on type
        if self.selected_analysis_type == 'correlation':
            self.handler.run_correlation_analysis(self.current_project_id, config)
        elif self.selected_analysis_type == 't_test':
            self.handler.run_t_test(self.current_project_id, config)
        elif self.selected_analysis_type == 'anova':
            self.handler.run_anova(self.current_project_id, config)
        elif self.selected_analysis_type == 'regression':
            self.handler.run_regression(self.current_project_id, config)
        elif self.selected_analysis_type == 'chi_square':
            self.handler.run_chi_square_test(self.current_project_id, config)
        elif self.selected_analysis_type == 'nonparametric':
            self.handler.run_nonparametric_test(self.current_project_id, config)
        elif self.selected_analysis_type == 'bayesian':
            self.handler.run_bayesian_t_test(self.current_project_id, config)
        elif self.selected_analysis_type == 'effect_size':
            self.handler.calculate_effect_size(self.current_project_id, config)
        elif self.selected_analysis_type == 'power_analysis':
            self.handler.run_power_analysis(self.current_project_id, config)
        elif self.selected_analysis_type == 'confidence_intervals':
            self.handler.calculate_confidence_intervals(self.current_project_id, config)
        elif self.selected_analysis_type == 'multiple_comparisons':
            self.handler.run_multiple_comparisons(self.current_project_id, config)
        else:
            toast("Analysis type not implemented yet")
    
    def prepare_analysis_config(self):
        """Prepare configuration for analysis"""
        config = {
            'variables': list(self.selected_variables),
            'method': self.selected_test_method,
            'significance_level': float(self.significance_level) if self.significance_level else 0.05,
            'confidence_level': float(self.confidence_level) if self.confidence_level else 0.95,
        }
        
        # Add specific configurations based on analysis type
        if self.selected_analysis_type in ['t_test', 'anova']:
            # Get dependent and independent variables from UI
            config['dependent_variable'] = self.get_dependent_variable()
            config['independent_variable'] = self.get_independent_variable()
            config['independent_variables'] = self.get_independent_variables()
        
        elif self.selected_analysis_type == 'regression':
            config['dependent_variable'] = self.get_dependent_variable()
            config['independent_variables'] = list(self.selected_variables)
            config['regression_type'] = self.selected_test_method
        
        elif self.selected_analysis_type == 'chi_square':
            variables = list(self.selected_variables)
            config['variable1'] = variables[0] if len(variables) > 0 else None
            config['variable2'] = variables[1] if len(variables) > 1 else None
            config['test_type'] = self.selected_test_method
        
        elif self.selected_analysis_type == 'effect_size':
            config['dependent_variable'] = self.get_dependent_variable()
            config['independent_variable'] = self.get_independent_variable()
            config['effect_size_measure'] = self.selected_test_method
        
        return config
    
    def get_dependent_variable(self):
        """Get selected dependent variable"""
        # This would be implemented based on UI selection
        # For now, return first selected variable
        return list(self.selected_variables)[0] if self.selected_variables else None
    
    def get_independent_variable(self):
        """Get selected independent variable"""
        # This would be implemented based on UI selection
        # For now, return second selected variable
        variables = list(self.selected_variables)
        return variables[1] if len(variables) > 1 else None
    
    def get_independent_variables(self):
        """Get selected independent variables"""
        # This would be implemented based on UI selection
        # For now, return all but first selected variable
        variables = list(self.selected_variables)
        return variables[1:] if len(variables) > 1 else []
    
    def clear_analysis(self):
        """Clear current analysis and results"""
        self.selected_analysis_type = ""
        self.selected_test_method = ""
        self.selected_variables = set()
        self.analysis_results = {}
        self.current_analysis_type = ""
        
        # Clear all result objects
        self.correlation_results = {}
        self.t_test_results = {}
        self.anova_results = {}
        self.regression_results = {}
        self.chi_square_results = {}
        self.nonparametric_results = {}
        self.bayesian_results = {}
        self.effect_size_results = {}
        self.power_analysis_results = {}
        self.confidence_intervals_results = {}
        self.multiple_comparisons_results = {}
        
        toast("Analysis cleared")
    
    def export_results(self):
        """Export analysis results"""
        if not self.analysis_results:
            toast("No results to export")
            return
        
        # This would implement result export functionality
        toast("Export functionality coming soon")
    
    def set_loading(self, loading):
        """Set loading state"""
        self.is_loading = loading
        
        # Update loading overlay
        if hasattr(self.ids, 'loading_overlay'):
            if loading:
                self.ids.loading_overlay.show()
            else:
                self.ids.loading_overlay.hide()
    
    def get_current_results(self):
        """Get current analysis results based on type"""
        results_map = {
            'correlation': self.correlation_results,
            't_test': self.t_test_results,
            'anova': self.anova_results,
            'regression': self.regression_results,
            'chi_square': self.chi_square_results,
            'nonparametric': self.nonparametric_results,
            'bayesian': self.bayesian_results,
            'effect_size': self.effect_size_results,
            'power_analysis': self.power_analysis_results,
            'confidence_intervals': self.confidence_intervals_results,
            'multiple_comparisons': self.multiple_comparisons_results
        }
        
        return results_map.get(self.current_analysis_type, {})
    
    def format_result_value(self, value, decimals=4):
        """Format result value for display"""
        if isinstance(value, (int, float)):
            return f"{value:.{decimals}f}"
        return str(value)
    
    def set_significance_level(self, value):
        """Set significance level from text field"""
        self.significance_level = value
    
    def set_confidence_level(self, value):
        """Set confidence level from text field"""
        self.confidence_level = value
    
    def on_enter(self):
        """Called when entering the screen"""
        if not self.analytics_service:
            self.init_screen(0)
    
    def on_leave(self):
        """Called when leaving the screen"""
        # Clean up any resources if needed
        pass