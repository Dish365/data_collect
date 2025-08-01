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
from services.descriptive_analytics import DescriptiveAnalyticsHandler
from services.distribution_analytics import DistributionAnalyticsHandler
from services.categorical_analytics import CategoricalAnalyticsHandler

# KV file loaded by main app after theme initialization

class DescriptiveAnalyticsScreen(Screen):
    """Descriptive Analytics Screen - handles UI interactions and delegates logic to service"""
    
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
    analysis_options = ListProperty([])
    sample_size_recommendations = ListProperty([])
    
    # Results state
    basic_statistics_data = ObjectProperty({})
    data_quality_data = ObjectProperty({})
    comprehensive_report_data = ObjectProperty({})
    distribution_results = ObjectProperty({})
    categorical_results = ObjectProperty({})
    
    # UI references
    project_menu = None
    variable_selection_dialog = None
    analysis_options_dialog = None
    results_dialog = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        
        # Initialize services
        self.auth_service = getattr(app, 'auth_service', None)
        self.analytics_service = getattr(app, 'analytics_service', None)
        
        # Initialize descriptive analytics service
        if self.analytics_service:
            self.descriptive_handler = DescriptiveAnalyticsHandler(
                self.analytics_service, self
            )
            self.distribution_handler = DistributionAnalyticsHandler(
                self.analytics_service, self
            )
            self.categorical_handler = CategoricalAnalyticsHandler(
                self.analytics_service, self
            )
        else:
            print("Warning: Analytics service not available")
            self.descriptive_handler = None
            self.distribution_handler = None
            self.categorical_handler = None
        
        # Initialize state
        self.analysis_results = {}
        self.selected_variables = set()
        self.analysis_options = []
        self.sample_size_recommendations = []
        self.basic_statistics_data = {}
        self.data_quality_data = {}
        self.comprehensive_report_data = {}
        
        # Initialize loading overlay
        self.loading_overlay = LoadingOverlay()
        
        # Bind to window resize for responsive updates
        Window.bind(size=self.on_window_resize)

    def on_enter(self):
        """Called when the screen is entered"""
        if hasattr(self.ids, 'top_bar') and self.ids.top_bar:
            self.ids.top_bar.set_title("Descriptive Analytics")
            self.ids.top_bar.set_current_screen("descriptive_analytics")
        
        # Initialize responsive layout
        self.update_responsive_layout()
        
        # Load projects and analysis options
        self.load_projects()
        self.load_analysis_options()

    def on_window_resize(self, window, size):
        """Handle window resize for responsive layout adjustments"""
        try:
            Clock.schedule_once(lambda dt: self.update_responsive_layout(), 0.1)
        except Exception as e:
            print(f"Error handling window resize in descriptive analytics: {e}")

    def update_responsive_layout(self):
        """Update layout based on current screen size"""
        try:
            if hasattr(self.ids, 'main_content'):
                width = Window.width
                
                # Adjust padding based on screen size
                if width < 768:  # Mobile
                    self.ids.main_content.padding = [dp(12), dp(8), dp(12), dp(20)]
                    self.ids.main_content.spacing = dp(12)
                elif width < 1024:  # Tablet
                    self.ids.main_content.padding = [dp(20), dp(12), dp(20), dp(24)]
                    self.ids.main_content.spacing = dp(16)
                else:  # Desktop
                    self.ids.main_content.padding = [dp(32), dp(16), dp(32), dp(28)]
                    self.ids.main_content.spacing = dp(20)
                
        except Exception as e:
            print(f"Error updating responsive layout: {e}")

    def load_projects(self):
        """Load available projects for selection"""
        try:
            if not self.auth_service:
                toast("Authentication service not available")
                return
            
            def load_projects_thread():
                try:
                    # Get projects from local database
                    projects = self.auth_service.get_user_projects()
                    
                    Clock.schedule_once(
                        lambda dt: self._handle_projects_loaded(projects), 0.1
                    )
                except Exception as e:
                    Clock.schedule_once(
                        lambda dt: toast(f"Failed to load projects: {str(e)}"), 0.1
                    )
            
            threading.Thread(target=load_projects_thread, daemon=True).start()
            
        except Exception as e:
            toast(f"Error loading projects: {str(e)}")

    def _handle_projects_loaded(self, projects):
        """Handle loaded projects"""
        try:
            self.project_list = []
            self.project_map = {}
            
            for project in projects:
                project_name = project.get('name', 'Unnamed Project')
                project_id = project.get('id', '')
                
                self.project_list.append(project_name)
                self.project_map[project_name] = project_id
            
            # Update project selector
            if hasattr(self.ids, 'project_selector'):
                if self.project_list:
                    self.ids.project_selector.text = "Select Project"
                else:
                    self.ids.project_selector.text = "No Projects Available"
                    
        except Exception as e:
            toast(f"Error processing projects: {str(e)}")

    def load_analysis_options(self):
        """Load available analysis options"""
        if not self.descriptive_handler:
            return
        
        # Get analysis options for current project (or general options)
        project_id = self.current_project_id or "default"
        self.analysis_options = self.descriptive_handler.get_analysis_options(project_id)

    def show_project_menu(self):
        """Show project selection menu"""
        if not self.project_list:
            toast("No projects available")
            return
        
        menu_items = []
        for project_name in self.project_list:
            menu_items.append({
                "viewclass": "MDListItem",
                "text": project_name,
                "height": dp(48),
                "on_release": lambda x=project_name: self.select_project(x)
            })
        
        self.project_menu = MDDropdownMenu(
            caller=self.ids.project_selector,
            items=menu_items,
            width=dp(200),
            max_height=dp(300)
        )
        self.project_menu.open()

    def select_project(self, project_name: str):
        """Select a project and load its analysis options"""
        if hasattr(self, 'project_menu') and self.project_menu:
            self.project_menu.dismiss()
        
        project_id = self.project_map.get(project_name)
        if not project_id:
            toast("Invalid project selection")
            return
        
        self.current_project_id = project_id
        self.current_project_name = project_name
        
        # Update UI
        if hasattr(self.ids, 'project_selector'):
            self.ids.project_selector.text = project_name
        
        # Clear previous results and load new options
        self.clear_results()
        self.load_analysis_options()
        self.load_sample_size_recommendations()

    def run_descriptive_analysis(self):
        """Run comprehensive descriptive analysis for selected project"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.descriptive_handler:
            toast("Descriptive analytics service not available")
            return
        
        # Delegate to service
        analysis_config = {'variables': list(self.selected_variables)} if self.selected_variables else None
        self.descriptive_handler.run_descriptive_analysis(self.current_project_id, analysis_config)

    def run_specific_analysis(self, analysis_option: Dict):
        """Run specific analysis type"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.descriptive_handler:
            toast("Descriptive analytics service not available")
            return
        
        endpoint = analysis_option.get('endpoint')
        name = analysis_option.get('name')
        
        if not endpoint or not name:
            toast("Invalid analysis option")
            return
        
        self.current_analysis_type = name
        self.descriptive_handler.run_specific_analysis(self.current_project_id, endpoint, name)

    def run_comprehensive_report(self):
        """Run comprehensive descriptive report"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.descriptive_handler:
            toast("Descriptive analytics service not available")
            return
        
        self.descriptive_handler.run_comprehensive_report(self.current_project_id)

    def show_variable_selection_dialog(self):
        """Show variable selection dialog"""
        if not self.project_variables:
            toast("No variables available for selection")
            return
        
        # This will be handled by the .kv file dialog
        if hasattr(self.ids, 'variable_selection_dialog'):
            self.ids.variable_selection_dialog.open()

    def show_analysis_options_dialog(self):
        """Show analysis options dialog"""
        if not self.analysis_options:
            toast("No analysis options available")
            return
        
        # This will be handled by the .kv file dialog
        if hasattr(self.ids, 'analysis_options_dialog'):
            self.ids.analysis_options_dialog.open()

    def show_sample_size_recommendations(self):
        """Show sample size recommendations"""
        if not self.descriptive_handler:
            toast("Descriptive analytics service not available")
            return
        
        self.descriptive_handler.show_sample_size_recommendations(self.current_project_id)

    def toggle_variable_selection(self, variable: str, active: bool):
        """Toggle variable selection"""
        if not self.descriptive_handler:
            return
        
        self.descriptive_handler.update_variable_selection(variable, active)
        
        # Update local state
        if active:
            self.selected_variables.add(variable)
        else:
            self.selected_variables.discard(variable)
        
        # Update selection info
        self.update_variable_selection_info()

    def select_all_variables(self):
        """Select all available variables"""
        self.selected_variables = set(self.project_variables)
        
        # Update service state
        if self.descriptive_handler:
            self.descriptive_handler.selected_variables = list(self.selected_variables)
        
        self.update_variable_selection_info()

    def clear_variable_selection(self):
        """Clear all variable selections"""
        self.selected_variables.clear()
        
        # Update service state
        if self.descriptive_handler:
            self.descriptive_handler.selected_variables = []
        
        self.update_variable_selection_info()

    def run_analysis_with_selected_variables(self):
        """Run analysis with selected variables"""
        if not self.descriptive_handler:
            toast("Descriptive analytics service not available")
            return
        
        self.descriptive_handler.run_analysis_with_selected_vars()

    def export_results(self, analysis_name: str = "Descriptive Analysis"):
        """Export analysis results"""
        if not self.analysis_results:
            toast("No results to export")
            return
        
        if not self.descriptive_handler:
            toast("Descriptive analytics service not available")
            return
        
        self.descriptive_handler.export_analysis_results(self.analysis_results, analysis_name)

    def export_sample_size_analysis(self):
        """Export sample size analysis"""
        if not self.descriptive_handler:
            toast("Descriptive analytics service not available")
            return
        
        sample_adequacy = {
            'recommendations': self.sample_size_recommendations,
            'project_id': self.current_project_id,
            'timestamp': Clock.get_time()
        }
        
        self.descriptive_handler.export_sample_size_analysis(sample_adequacy)

    def clear_results(self):
        """Clear all analysis results and reset state"""
        self.analysis_results = {}
        self.basic_statistics_data = {}
        self.data_quality_data = {}
        self.comprehensive_report_data = {}
        self.current_analysis_type = ""
        
        # Update UI
        self.update_results_display({})

    def load_sample_size_recommendations(self):
        """Load sample size recommendations for current project"""
        if not self.descriptive_handler or not self.current_project_id:
            return
        
        self.sample_size_recommendations = self.descriptive_handler.get_sample_size_recommendations(
            self.current_project_id
        )

    # UI update methods (called by service)
    def set_loading(self, loading: bool):
        """Set loading state"""
        self.is_loading = loading
        
        if loading and self.loading_overlay:
            self.add_widget(self.loading_overlay)
        elif self.loading_overlay in self.children:
            self.remove_widget(self.loading_overlay)

    def display_descriptive_results(self, results: Dict):
        """Display descriptive analysis results - called by service"""
        self.analysis_results = results
        
        # Update UI displays
        self.update_results_display(results)
        
        # Show success message
        toast("Descriptive analysis completed")

    def display_specific_analysis_results(self, results: Dict, analysis_name: str):
        """Display specific analysis results - called by service"""
        # Store results based on analysis type
        if 'basic' in analysis_name.lower() or 'statistics' in analysis_name.lower():
            self.basic_statistics_data = self.descriptive_handler.get_basic_statistics_data(results)
        elif 'quality' in analysis_name.lower():
            self.data_quality_data = self.descriptive_handler.get_data_quality_data(results)
        
        # Update main results
        self.analysis_results[analysis_name] = results
        
        # Update UI
        self.update_results_display(self.analysis_results)
        
        # Show results dialog
        self.show_results_dialog(analysis_name, results)

    def display_comprehensive_report_results(self, results: Dict):
        """Display comprehensive report results - called by service"""
        self.comprehensive_report_data = self.descriptive_handler.get_comprehensive_report_data(results)
        self.analysis_results['comprehensive_report'] = results
        
        # Update UI
        self.update_results_display(self.analysis_results)
        
        toast("Comprehensive report generated")

    def show_descriptive_variable_selection_ui(self, project_id: str):
        """Show descriptive variable selection UI - called by service"""
        # Load project variables first
        if self.analytics_service:
            try:
                variables = self.analytics_service.get_project_variables(project_id)
                if variables and 'error' not in variables:
                    # Extract variable names from the structure
                    all_vars = []
                    if isinstance(variables, dict):
                        for var_type, var_list in variables.items():
                            if isinstance(var_list, list):
                                all_vars.extend(var_list)
                    elif isinstance(variables, list):
                        all_vars = variables
                    
                    self.project_variables = all_vars
                    self.show_variable_selection_dialog()
                else:
                    toast("Failed to load project variables")
            except Exception as e:
                toast(f"Error loading variables: {str(e)}")

    def show_sample_size_recommendations_ui(self, recommendations: List[Dict]):
        """Show sample size recommendations UI - called by service"""
        self.sample_size_recommendations = recommendations
        
        # Update UI display
        if hasattr(self.ids, 'sample_size_content'):
            # This will be handled by property binding in KV
            pass

    def show_results_dialog(self, analysis_type: str, results: Dict):
        """Show detailed results dialog"""
        self.current_analysis_type = analysis_type
        
        # Update results display
        self.update_results_display({analysis_type: results})
        
        # This will be handled by the .kv file dialog
        if hasattr(self.ids, 'results_dialog'):
            self.ids.results_dialog.open()

    def update_results_display(self, results: Dict):
        """Update results display in UI"""
        try:
            # Update main results area
            if hasattr(self.ids, 'results_content'):
                # This will be bound to the analysis_results property in KV
                pass
            
            # Update status indicators
            if hasattr(self.ids, 'analysis_status_label'):
                if results:
                    self.ids.analysis_status_label.text = "Status: Analysis Complete"
                else:
                    self.ids.analysis_status_label.text = "Status: Ready"
            
            # Update analysis count
            if hasattr(self.ids, 'analysis_count_label'):
                count = len(results)
                self.ids.analysis_count_label.text = f"{count} analyses completed"
                
        except Exception as e:
            print(f"Error updating results display: {e}")

    def update_variable_selection_info(self):
        """Update variable selection information"""
        try:
            if hasattr(self.ids, 'variable_selection_info_label'):
                count = len(self.selected_variables)
                total = len(self.project_variables)
                self.ids.variable_selection_info_label.text = f"{count}/{total} variables selected"
                
        except Exception as e:
            print(f"Error updating variable selection info: {e}")

    def show_error(self, error_message: str):
        """Show error message"""
        toast(error_message)
        
        # Update error display in UI if needed
        if hasattr(self.ids, 'error_label'):
            self.ids.error_label.text = error_message

    def show_success(self, message: str):
        """Show success message"""
        toast(message)

    # Quick analysis methods
    def run_basic_statistics(self):
        """Run basic statistics analysis"""
        analysis_option = {
            'name': 'Basic Statistics',
            'endpoint': 'basic-statistics'
        }
        self.run_specific_analysis(analysis_option)

    def run_distribution_analysis(self):
        """Run distribution analysis"""
        analysis_option = {
            'name': 'Distribution Analysis',
            'endpoint': 'distributions'
        }
        self.run_specific_analysis(analysis_option)

    def run_categorical_analysis(self):
        """Run categorical analysis"""
        analysis_option = {
            'name': 'Categorical Analysis',
            'endpoint': 'categorical'
        }
        self.run_specific_analysis(analysis_option)

    def run_outlier_analysis(self):
        """Run outlier detection analysis"""
        analysis_option = {
            'name': 'Outlier Detection',
            'endpoint': 'outliers'
        }
        self.run_specific_analysis(analysis_option)

    def run_missing_data_analysis(self):
        """Run missing data analysis"""
        analysis_option = {
            'name': 'Missing Data Analysis',
            'endpoint': 'missing-data'
        }
        self.run_specific_analysis(analysis_option)

    def run_data_quality_analysis(self):
        """Run data quality assessment"""
        analysis_option = {
            'name': 'Data Quality Assessment',
            'endpoint': 'data-quality'
        }
        self.run_specific_analysis(analysis_option)

    # Export methods
    def export_to_json(self):
        """Export results to JSON"""
        self.export_results("Descriptive Analysis")

    def export_to_csv(self):
        """Export results to CSV"""
        toast("CSV export coming soon")

    def share_results(self):
        """Share analysis results"""
        toast("Share functionality coming soon")

    # Utility methods
    def get_selected_variables_list(self) -> List[str]:
        """Get list of selected variables"""
        return list(self.selected_variables)

    def get_analysis_summary(self) -> str:
        """Get analysis summary text"""
        if not self.analysis_results:
            return "No analysis completed yet"
        
        count = len(self.analysis_results)
        summary = f"Completed {count} descriptive analyses"
        
        if self.selected_variables:
            summary += f" on {len(self.selected_variables)} variables"
        
        return summary

    def is_analysis_complete(self) -> bool:
        """Check if analysis is complete"""
        return bool(self.analysis_results and not self.is_loading)

    def has_sample_recommendations(self) -> bool:
        """Check if there are sample size recommendations available"""
        return bool(self.sample_size_recommendations)

    # Distribution Analysis Methods
    def display_distribution_results(self, results: Dict):
        """Display distribution analysis results - called by distribution handler"""
        self.distribution_results = results
        self.analysis_results['distribution_analysis'] = results
        
        # Update UI
        self.update_results_display(self.analysis_results)
        
        toast("Distribution analysis completed")

    def show_distribution_variable_selection(self, numeric_vars: List[str]):
        """Show distribution variable selection UI - called by distribution handler"""
        self.project_variables = numeric_vars
        self.show_variable_selection_dialog()

    def run_distribution_with_selected_variables(self):
        """Run distribution analysis with selected variables"""
        if not self.distribution_handler:
            toast("Distribution analytics service not available")
            return
        
        self.distribution_handler.run_distribution_with_selected_vars()

    # Categorical Analysis Methods
    def display_categorical_results(self, results: Dict):
        """Display categorical analysis results - called by categorical handler"""
        self.categorical_results = results
        self.analysis_results['categorical_analysis'] = results
        
        # Update UI
        self.update_results_display(self.analysis_results)
        
        toast("Categorical analysis completed")

    def show_categorical_variable_selection_ui(self, project_id: str):
        """Show categorical variable selection UI - called by categorical handler"""
        # Load categorical variables and show selection dialog
        if self.analytics_service:
            try:
                variables = self.analytics_service.get_project_variables(project_id)
                if variables and 'error' not in variables:
                    categorical_vars = variables.get('categorical', [])
                    self.project_variables = categorical_vars
                    self.show_variable_selection_dialog()
                else:
                    toast("Failed to load categorical variables")
            except Exception as e:
                toast(f"Error loading variables: {str(e)}")

    def show_categorical_variable_selection(self, categorical_vars: List[str]):
        """Show categorical variable selection - called by categorical handler"""
        self.project_variables = categorical_vars
        self.show_variable_selection_dialog()

    def run_categorical_additional_analysis(self, analysis_type: str):
        """Run additional categorical analysis - called by categorical handler"""
        if analysis_type == 'chi_square':
            toast("Running Chi-Square test...")
        elif analysis_type == 'cramers_v':
            toast("Running Cramer's V analysis...")
        elif analysis_type == 'frequency':
            toast("Running frequency analysis...")
        
        # Delegate to categorical handler
        if self.categorical_handler:
            self.categorical_handler.run_additional_analysis(analysis_type)

    def run_categorical_with_selected_variables(self):
        """Run categorical analysis with selected variables"""
        if not self.categorical_handler:
            toast("Categorical analytics service not available")
            return
        
        self.categorical_handler.run_categorical_with_selected_vars()

    # Extended Analysis Methods
    def run_distribution_analysis_extended(self, variables: List[str] = None):
        """Run extended distribution analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.distribution_handler:
            toast("Distribution analytics service not available")
            return
        
        self.distribution_handler.run_distribution_analysis(self.current_project_id, variables)

    def run_categorical_analysis_extended(self, variables: List[str] = None):
        """Run extended categorical analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.categorical_handler:
            toast("Categorical analytics service not available")
            return
        
        self.categorical_handler.run_categorical_analysis(self.current_project_id, variables)

    def switch_results_tab(self, tab_name: str):
        """Switch between different result tabs"""
        try:
            # Update tab button colors - reset all to inactive
            tab_ids = ['statistics_tab', 'distribution_tab', 'categorical_tab', 
                      'geospatial_tab', 'temporal_tab', 'quality_tab', 'report_tab']
            
            for tab_id in tab_ids:
                if hasattr(self.ids, tab_id):
                    getattr(self.ids, tab_id).text_color = (0.6, 0.6, 0.6, 1)
            
            # Activate selected tab
            active_tab_id = f"{tab_name}_tab"
            if hasattr(self.ids, active_tab_id):
                app = App.get_running_app()
                getattr(self.ids, active_tab_id).text_color = app.theme_cls.primaryColor
            
            # Update results display based on tab
            self.update_results_display_for_tab(tab_name)
            
        except Exception as e:
            print(f"Error switching results tab: {e}")

    def update_results_display_for_tab(self, tab_name: str):
        """Update results display based on selected tab"""
        try:
            # This method can be extended to show different content based on the selected tab
            if tab_name == "statistics":
                # Show basic statistics
                if self.basic_statistics_data:
                    self.update_results_display({'basic_statistics': self.basic_statistics_data})
            elif tab_name == "distribution":
                # Show distribution results
                if self.distribution_results:
                    self.update_results_display({'distribution': self.distribution_results})
            elif tab_name == "categorical":
                # Show categorical results
                if self.categorical_results:
                    self.update_results_display({'categorical': self.categorical_results})
            elif tab_name == "geospatial":
                # Show geospatial results  
                if 'geospatial_analysis' in self.analysis_results:
                    self.update_results_display({'geospatial': self.analysis_results['geospatial_analysis']})
            elif tab_name == "temporal":
                # Show temporal results
                if 'temporal_analysis' in self.analysis_results:
                    self.update_results_display({'temporal': self.analysis_results['temporal_analysis']})
            elif tab_name == "quality":
                # Show data quality results
                if self.data_quality_data:
                    self.update_results_display({'data_quality': self.data_quality_data})
            elif tab_name == "report":
                # Show comprehensive report
                if self.comprehensive_report_data:
                    self.update_results_display({'comprehensive_report': self.comprehensive_report_data})
                elif 'executive_summary' in self.analysis_results:
                    self.update_results_display({'executive_summary': self.analysis_results['executive_summary']})
                    
        except Exception as e:
            print(f"Error updating results display for tab: {e}")

    # ===== NEW ADVANCED ANALYTICS METHODS =====

    # Geospatial Analysis Methods
    def run_geospatial_analysis(self, lat_column: str, lon_column: str, 
                               value_column: str = None, max_distance_km: float = 10.0,
                               n_clusters: int = 5):
        """Run geospatial analysis for the project"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.descriptive_handler:
            toast("Descriptive analytics service not available")
            return
        
        self.descriptive_handler.run_geospatial_analysis(
            self.current_project_id, lat_column, lon_column, value_column, max_distance_km, n_clusters
        )

    def display_geospatial_results(self, results: Dict):
        """Display geospatial analysis results - called by service"""
        self.analysis_results['geospatial_analysis'] = results
        self.update_results_display(self.analysis_results)
        toast("Geospatial analysis completed")

    # Temporal Analysis Methods
    def run_temporal_analysis(self, date_column: str, value_columns: List[str] = None,
                             detect_seasonal: bool = True, seasonal_period: int = None):
        """Run temporal analysis for the project"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.descriptive_handler:
            toast("Descriptive analytics service not available")
            return
        
        self.descriptive_handler.run_temporal_analysis(
            self.current_project_id, date_column, value_columns, detect_seasonal, seasonal_period
        )

    def display_temporal_results(self, results: Dict):
        """Display temporal analysis results - called by service"""
        self.analysis_results['temporal_analysis'] = results
        self.update_results_display(self.analysis_results)
        toast("Temporal analysis completed")

    # Weighted Statistics Methods
    def run_weighted_statistics(self, value_column: str, weight_column: str):
        """Run weighted statistics analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.descriptive_handler:
            toast("Descriptive analytics service not available")
            return
        
        self.descriptive_handler.run_weighted_statistics(
            self.current_project_id, value_column, weight_column
        )

    def display_weighted_statistics_results(self, results: Dict):
        """Display weighted statistics results - called by service"""
        self.analysis_results['weighted_statistics'] = results
        self.update_results_display(self.analysis_results)
        toast("Weighted statistics completed")

    # Grouped Statistics Methods
    def run_grouped_statistics(self, group_by: Union[str, List[str]], 
                              target_columns: List[str] = None,
                              stats_functions: List[str] = None):
        """Run grouped statistics analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.descriptive_handler:
            toast("Descriptive analytics service not available")
            return
        
        self.descriptive_handler.run_grouped_statistics(
            self.current_project_id, group_by, target_columns, stats_functions
        )

    def display_grouped_statistics_results(self, results: Dict):
        """Display grouped statistics results - called by service"""
        self.analysis_results['grouped_statistics'] = results
        self.update_results_display(self.analysis_results)
        toast("Grouped statistics completed")

    # Missing Patterns Methods
    def run_missing_patterns_analysis(self, max_patterns: int = 20, group_column: str = None):
        """Run missing data patterns analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.descriptive_handler:
            toast("Descriptive analytics service not available")
            return
        
        self.descriptive_handler.run_missing_patterns_analysis(
            self.current_project_id, max_patterns, group_column
        )

    def display_missing_patterns_results(self, results: Dict):
        """Display missing patterns results - called by service"""
        self.analysis_results['missing_patterns'] = results
        self.update_results_display(self.analysis_results)
        toast("Missing patterns analysis completed")

    # Executive Summary Methods
    def generate_executive_summary(self):
        """Generate executive summary report"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.descriptive_handler:
            toast("Descriptive analytics service not available")
            return
        
        self.descriptive_handler.generate_executive_summary(self.current_project_id)

    def display_executive_summary_results(self, results: Dict):
        """Display executive summary results - called by service"""
        self.analysis_results['executive_summary'] = results
        self.update_results_display(self.analysis_results)
        toast("Executive summary generated")

    # Export Report Methods
    def export_analysis_report(self, format: str = 'json', analysis_type: str = 'comprehensive',
                              include_metadata: bool = True):
        """Export analysis report in specified format"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.descriptive_handler:
            toast("Descriptive analytics service not available")
            return
        
        self.descriptive_handler.export_analysis_report(
            self.current_project_id, format, analysis_type, include_metadata
        )

    def display_export_report_results(self, results: Dict, format: str):
        """Display export report results - called by service"""
        if 'content' in results:
            # Save or display the exported content
            content = results['content']
            if format == 'json':
                toast("JSON report generated successfully")
            elif format == 'html':
                toast("HTML report generated successfully")
            elif format == 'markdown':
                toast("Markdown report generated successfully")
            
            # Store the exported content for further use
            self.analysis_results['exported_report'] = {
                'format': format,
                'content': content
            }

    # Cross-Tabulation Methods (Categorical)
    def run_cross_tabulation(self, var1: str, var2: str, normalize: str = None):
        """Run cross-tabulation analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.categorical_handler:
            toast("Categorical analytics service not available")
            return
        
        self.categorical_handler.run_cross_tabulation(
            self.current_project_id, var1, var2, normalize
        )

    def display_cross_tabulation_results(self, results: Dict):
        """Display cross-tabulation results - called by service"""
        self.analysis_results['cross_tabulation'] = results
        self.update_results_display(self.analysis_results)
        toast("Cross-tabulation analysis completed")

    # Diversity Metrics Methods (Categorical)
    def run_diversity_metrics(self, variables: List[str] = None):
        """Run diversity metrics analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.categorical_handler:
            toast("Categorical analytics service not available")
            return
        
        self.categorical_handler.run_diversity_metrics(self.current_project_id, variables)

    def display_diversity_metrics_results(self, results: Dict):
        """Display diversity metrics results - called by service"""
        self.analysis_results['diversity_metrics'] = results
        self.update_results_display(self.analysis_results)
        toast("Diversity metrics analysis completed")

    # Categorical Associations Methods
    def run_categorical_associations(self, variables: List[str] = None, method: str = 'cramers_v'):
        """Run categorical associations analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.categorical_handler:
            toast("Categorical analytics service not available")
            return
        
        self.categorical_handler.run_categorical_associations(
            self.current_project_id, variables, method
        )

    def display_categorical_associations_results(self, results: Dict):
        """Display categorical associations results - called by service"""
        self.analysis_results['categorical_associations'] = results
        self.update_results_display(self.analysis_results)
        toast("Categorical associations analysis completed")

    # Normality Testing Methods (Distribution)
    def run_normality_tests(self, variables: List[str] = None, alpha: float = 0.05):
        """Run comprehensive normality tests"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.distribution_handler:
            toast("Distribution analytics service not available")
            return
        
        self.distribution_handler.run_normality_tests(self.current_project_id, variables, alpha)

    def display_normality_tests_results(self, results: Dict):
        """Display normality tests results - called by service"""
        self.analysis_results['normality_tests'] = results
        self.update_results_display(self.analysis_results)
        toast("Normality tests completed")

    # Distribution Fitting Methods
    def run_distribution_fitting(self, variables: List[str] = None, 
                                distributions: List[str] = None):
        """Run distribution fitting analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.distribution_handler:
            toast("Distribution analytics service not available")
            return
        
        self.distribution_handler.run_distribution_fitting(
            self.current_project_id, variables, distributions
        )

    def display_distribution_fitting_results(self, results: Dict):
        """Display distribution fitting results - called by service"""
        self.analysis_results['distribution_fitting'] = results
        self.update_results_display(self.analysis_results)
        toast("Distribution fitting completed")

    # Advanced Analysis Menu Methods
    def show_advanced_analysis_menu(self):
        """Show advanced analysis options menu"""
        if hasattr(self.ids, 'advanced_analysis_dialog'):
            self.ids.advanced_analysis_dialog.open()

    def show_geospatial_dialog(self):
        """Show geospatial analysis parameter dialog"""
        if hasattr(self.ids, 'geospatial_dialog'):
            self.ids.geospatial_dialog.open()

    def show_temporal_dialog(self):
        """Show temporal analysis parameter dialog"""
        if hasattr(self.ids, 'temporal_dialog'):
            self.ids.temporal_dialog.open()

    def show_cross_tabulation_dialog(self):
        """Show cross-tabulation parameter dialog"""
        if hasattr(self.ids, 'cross_tabulation_dialog'):
            self.ids.cross_tabulation_dialog.open()

    def show_weighted_stats_dialog(self):
        """Show weighted statistics parameter dialog"""
        if hasattr(self.ids, 'weighted_stats_dialog'):
            self.ids.weighted_stats_dialog.open()

    def show_export_options_dialog(self):
        """Show export options dialog"""
        if hasattr(self.ids, 'export_options_dialog'):
            self.ids.export_options_dialog.open()

    # Utility Methods for Advanced Analytics
    def get_numeric_variables(self) -> List[str]:
        """Get numeric variables from project"""
        if not self.analytics_service or not self.current_project_id:
            return []
        
        try:
            variables = self.analytics_service.get_project_variables(self.current_project_id)
            if variables and 'numeric' in variables:
                return variables['numeric']
        except Exception as e:
            print(f"Error getting numeric variables: {e}")
        
        return []

    def get_categorical_variables(self) -> List[str]:
        """Get categorical variables from project"""
        if not self.analytics_service or not self.current_project_id:
            return []
        
        try:
            variables = self.analytics_service.get_project_variables(self.current_project_id)
            if variables and 'categorical' in variables:
                return variables['categorical']
        except Exception as e:
            print(f"Error getting categorical variables: {e}")
        
        return []

    def get_datetime_variables(self) -> List[str]:
        """Get datetime variables from project"""
        if not self.analytics_service or not self.current_project_id:
            return []
        
        try:
            variables = self.analytics_service.get_project_variables(self.current_project_id)
            if variables and 'datetime' in variables:
                return variables['datetime']
        except Exception as e:
            print(f"Error getting datetime variables: {e}")
        
        return []

    def get_analysis_results_summary(self) -> Dict[str, Any]:
        """Get summary of all analysis results for display"""
        return {
            'total_analyses': len(self.analysis_results),
            'analyses_completed': list(self.analysis_results.keys()),
            'has_basic_stats': 'basic_statistics' in self.analysis_results,
            'has_distribution': 'distribution_analysis' in self.analysis_results,
            'has_categorical': 'categorical_analysis' in self.analysis_results,
            'has_geospatial': 'geospatial_analysis' in self.analysis_results,
            'has_temporal': 'temporal_analysis' in self.analysis_results,
            'has_executive_summary': 'executive_summary' in self.analysis_results,
        } 