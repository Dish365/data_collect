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
from typing import Dict, List, Any, Optional

from widgets.loading_overlay import LoadingOverlay
from services.auto_detection_analytics import AutoDetectionAnalyticsHandler

# KV file loaded by main app after theme initialization

class AutoDetectionScreen(Screen):
    """Auto Detection Screen - handles UI interactions and delegates logic to service"""
    
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
    data_characteristics = ObjectProperty({})
    recommendations = ListProperty([])
    available_analysis_types = ListProperty([])
    
    # UI references
    project_menu = None
    variable_selection_dialog = None
    analysis_type_dialog = None
    results_dialog = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        
        # Initialize services
        self.auth_service = getattr(app, 'auth_service', None)
        self.analytics_service = getattr(app, 'analytics_service', None)
        
        # Initialize auto detection service
        if self.analytics_service:
            self.auto_detection_handler = AutoDetectionAnalyticsHandler(
                self.analytics_service, self
            )
        else:
            print("Warning: Analytics service not available")
            self.auto_detection_handler = None
        
        # Initialize state
        self.analysis_results = {}
        self.selected_variables = set()
        self.data_characteristics = {}
        self.recommendations = []
        self.available_analysis_types = []
        
        # Initialize loading overlay
        self.loading_overlay = LoadingOverlay()
        
        # Bind to window resize for responsive updates
        Window.bind(size=self.on_window_resize)

    def on_enter(self):
        """Called when the screen is entered"""
        if hasattr(self.ids, 'top_bar') and self.ids.top_bar:
            self.ids.top_bar.set_title("Auto Detection Analytics")
        
        # Initialize responsive layout
        self.update_responsive_layout()
        
        # Load projects for selection
        self.load_projects()

    def on_window_resize(self, window, size):
        """Handle window resize for responsive layout adjustments"""
        try:
            Clock.schedule_once(lambda dt: self.update_responsive_layout(), 0.1)
        except Exception as e:
            print(f"Error handling window resize in auto detection: {e}")

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
        """Select a project and start auto detection"""
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
        
        # Clear previous results
        self.clear_results()

    def run_auto_detection(self):
        """Run auto detection analysis for selected project"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.auto_detection_handler:
            toast("Auto detection service not available")
            return
        
        # Delegate to service
        self.auto_detection_handler.run_auto_detection(self.current_project_id)

    def run_specific_analysis(self, analysis_type: str):
        """Run specific analysis type"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.auto_detection_handler:
            toast("Auto detection service not available")
            return
        
        self.current_analysis_type = analysis_type
        self.auto_detection_handler.run_specific_analysis(self.current_project_id, analysis_type)

    def run_analysis_with_variables(self, variables: List[str]):
        """Run analysis with selected variables"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.auto_detection_handler:
            toast("Auto detection service not available")
            return
        
        self.auto_detection_handler.run_analysis_with_selected_variables(
            self.current_project_id, variables
        )

    def show_variable_selection_dialog(self):
        """Show variable selection dialog"""
        if not self.project_variables:
            toast("No variables available for selection")
            return
        
        # This will be handled by the .kv file dialog
        if hasattr(self.ids, 'variable_selection_dialog'):
            self.ids.variable_selection_dialog.open()

    def show_analysis_type_dialog(self):
        """Show analysis type selection dialog"""
        if not self.available_analysis_types:
            toast("No analysis types available")
            return
        
        # This will be handled by the .kv file dialog
        if hasattr(self.ids, 'analysis_type_dialog'):
            self.ids.analysis_type_dialog.open()

    def show_results_dialog(self, analysis_type: str, results: Dict):
        """Show detailed results dialog"""
        self.current_analysis_type = analysis_type
        
        # Update results display
        self.update_results_display(results)
        
        # This will be handled by the .kv file dialog
        if hasattr(self.ids, 'results_dialog'):
            self.ids.results_dialog.open()

    def toggle_variable_selection(self, variable: str, active: bool):
        """Toggle variable selection"""
        if active:
            self.selected_variables.add(variable)
        else:
            self.selected_variables.discard(variable)
        
        # Update selection info
        self.update_variable_selection_info()

    def select_all_variables(self):
        """Select all available variables"""
        self.selected_variables = set(self.project_variables)
        self.update_variable_selection_info()

    def clear_variable_selection(self):
        """Clear all variable selections"""
        self.selected_variables.clear()
        self.update_variable_selection_info()

    def export_results(self):
        """Export analysis results"""
        if not self.analysis_results:
            toast("No results to export")
            return
        
        if not self.auto_detection_handler:
            toast("Auto detection service not available")
            return
        
        self.auto_detection_handler.export_analytics_results(self.analysis_results)

    def clear_results(self):
        """Clear all analysis results and reset state"""
        self.analysis_results = {}
        self.data_characteristics = {}
        self.recommendations = []
        self.project_variables = []
        self.selected_variables.clear()
        self.available_analysis_types = []
        self.current_analysis_type = ""
        
        # Update UI
        self.update_results_display({})
        self.update_variable_selection_info()

    def refresh_analysis(self):
        """Refresh the current analysis"""
        if self.current_project_id:
            self.run_auto_detection()
        else:
            toast("Please select a project first")

    # UI update methods (called by service)
    def set_loading(self, loading: bool):
        """Set loading state"""
        self.is_loading = loading
        
        if loading and self.loading_overlay:
            self.add_widget(self.loading_overlay)
        elif self.loading_overlay in self.children:
            self.remove_widget(self.loading_overlay)

    def update_analysis_results(self, results: Dict):
        """Update analysis results - called by service"""
        self.analysis_results = results
        
        # Extract key components
        self.data_characteristics = results.get('data_characteristics', {})
        self.recommendations = results.get('recommendations', [])
        self.project_variables = results.get('project_variables', [])
        self.available_analysis_types = results.get('available_analysis_types', [])
        
        # Update UI displays
        self.update_results_display(results)
        self.update_recommendations_display()
        self.update_data_overview_display()

    def update_results_display(self, results: Dict):
        """Update results display in UI"""
        try:
            # Update main results area
            if hasattr(self.ids, 'results_content'):
                # This will be bound to the analysis_results property in KV
                pass
            
            # Update status indicators
            if hasattr(self.ids, 'analysis_status_label'):
                status = results.get('status', 'No analysis run')
                self.ids.analysis_status_label.text = f"Status: {status}"
            
            # Update analysis count
            if hasattr(self.ids, 'analysis_count_label'):
                analyses = results.get('analyses', {})
                count = len(analyses)
                self.ids.analysis_count_label.text = f"{count} analyses completed"
                
        except Exception as e:
            print(f"Error updating results display: {e}")

    def update_recommendations_display(self):
        """Update recommendations display"""
        try:
            if hasattr(self.ids, 'recommendations_content'):
                # This will be bound to the recommendations property in KV
                pass
                
        except Exception as e:
            print(f"Error updating recommendations display: {e}")

    def update_data_overview_display(self):
        """Update data overview display"""
        try:
            if hasattr(self.ids, 'data_overview_content'):
                # Update data characteristics display
                if self.data_characteristics:
                    total_responses = self.data_characteristics.get('total_responses', 0)
                    total_questions = self.data_characteristics.get('total_questions', 0)
                    
                    if hasattr(self.ids, 'total_responses_label'):
                        self.ids.total_responses_label.text = f"{total_responses:,} responses"
                    if hasattr(self.ids, 'total_questions_label'):
                        self.ids.total_questions_label.text = f"{total_questions} questions"
                
        except Exception as e:
            print(f"Error updating data overview display: {e}")

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

    # Analysis action methods
    def run_correlation_analysis(self):
        """Run correlation analysis"""
        self.run_specific_analysis("correlation")

    def run_distribution_analysis(self):
        """Run distribution analysis"""
        self.run_specific_analysis("distribution")

    def run_outlier_analysis(self):
        """Run outlier analysis"""
        self.run_specific_analysis("outlier")

    def run_categorical_analysis(self):
        """Run categorical analysis"""
        self.run_specific_analysis("categorical")

    def run_missing_data_analysis(self):
        """Run missing data analysis"""
        self.run_specific_analysis("missing_data")

    def run_basic_statistics(self):
        """Run basic statistics analysis"""
        self.run_specific_analysis("basic_statistics")

    def run_comprehensive_analysis(self):
        """Run comprehensive analysis"""
        self.run_specific_analysis("comprehensive")

    # Recommendation actions
    def run_recommended_analysis(self, recommendation: Dict):
        """Run a recommended analysis"""
        if not self.auto_detection_handler:
            toast("Auto detection service not available")
            return
        
        self.auto_detection_handler.run_recommended_analysis(recommendation)

    def dismiss_recommendation(self, recommendation_id: str):
        """Dismiss a recommendation"""
        try:
            self.recommendations = [
                r for r in self.recommendations 
                if r.get('id') != recommendation_id
            ]
            self.update_recommendations_display()
            toast("Recommendation dismissed")
        except Exception as e:
            print(f"Error dismissing recommendation: {e}")

    # Export and sharing methods
    def export_to_json(self):
        """Export results to JSON"""
        self.export_results()

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
        
        analyses = self.analysis_results.get('analyses', {})
        recommendations = self.analysis_results.get('recommendations', [])
        
        summary = f"Completed {len(analyses)} analyses"
        if recommendations:
            summary += f", {len(recommendations)} recommendations available"
        
        return summary

    def is_analysis_complete(self) -> bool:
        """Check if analysis is complete"""
        return bool(self.analysis_results and not self.is_loading)

    def has_recommendations(self) -> bool:
        """Check if there are recommendations available"""
        return bool(self.recommendations) 