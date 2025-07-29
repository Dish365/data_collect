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
from services.qualitative_analytics import QualitativeAnalyticsHandler

Builder.load_file("kv/qualitative_analytics.kv")

class QualitativeAnalyticsScreen(Screen):
    """Qualitative Analytics Screen - handles UI interactions and delegates logic to service"""
    
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
    text_analysis_summary = ObjectProperty({})
    text_results_data = ObjectProperty({})
    sentiment_data = ObjectProperty({})
    theme_data = ListProperty([])
    word_frequency_data = ListProperty([])
    
    # UI references
    project_menu = None
    analysis_type_dialog = None
    results_dialog = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        
        # Initialize services
        self.auth_service = getattr(app, 'auth_service', None)
        self.analytics_service = getattr(app, 'analytics_service', None)
        
        # Initialize qualitative analytics service
        if self.analytics_service:
            self.qualitative_handler = QualitativeAnalyticsHandler(
                self.analytics_service, self
            )
        else:
            print("Warning: Analytics service not available")
            self.qualitative_handler = None
        
        # Initialize state
        self.analysis_results = {}
        self.text_analysis_summary = {}
        self.text_results_data = {}
        self.sentiment_data = {}
        self.theme_data = []
        self.word_frequency_data = []
        
        # Initialize loading overlay
        self.loading_overlay = LoadingOverlay()
        
        # Bind to window resize for responsive updates
        Window.bind(size=self.on_window_resize)

    def on_enter(self):
        """Called when the screen is entered"""
        if hasattr(self.ids, 'top_bar') and self.ids.top_bar:
            self.ids.top_bar.set_title("Qualitative Analytics")
        
        # Initialize responsive layout
        self.update_responsive_layout()
        
        # Load projects for selection
        self.load_projects()

    def on_window_resize(self, window, size):
        """Handle window resize for responsive layout adjustments"""
        try:
            Clock.schedule_once(lambda dt: self.update_responsive_layout(), 0.1)
        except Exception as e:
            print(f"Error handling window resize in qualitative analytics: {e}")

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
                "viewclass": "OneLineListItem",
                "text": project_name,
                "height": dp(48),
                "on_release": lambda x=project_name: self.select_project(x)
            })
        
        self.project_menu = MDDropdownMenu(
            caller=self.ids.project_selector,
            items=menu_items,
            width_mult=4,
            max_height=dp(300)
        )
        self.project_menu.open()

    def select_project(self, project_name: str):
        """Select a project and prepare for analysis"""
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

    def run_text_analysis(self):
        """Run text analysis for selected project"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        # Delegate to service
        self.qualitative_handler.run_text_analysis(self.current_project_id)

    def run_sentiment_analysis(self, text_fields: List[str] = None):
        """Run sentiment analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        self.qualitative_handler.run_sentiment_analysis(self.current_project_id, text_fields)

    def run_theme_analysis(self, text_fields: List[str] = None, num_themes: int = 5):
        """Run theme analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        self.qualitative_handler.run_theme_analysis(self.current_project_id, text_fields, num_themes)

    def show_sentiment_analysis(self):
        """Show sentiment analysis interface"""
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        self.qualitative_handler.show_sentiment_analysis()

    def show_theme_analysis(self):
        """Show theme analysis interface"""
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        self.qualitative_handler.show_theme_analysis()

    def show_detailed_text_results(self):
        """Show detailed text results"""
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        self.qualitative_handler.show_detailed_text_results(self.text_results_data)

    def export_text_results(self):
        """Export text analysis results"""
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        self.qualitative_handler.export_text_results(self.analysis_results)

    def clear_results(self):
        """Clear all analysis results and reset state"""
        self.analysis_results = {}
        self.text_analysis_summary = {}
        self.text_results_data = {}
        self.sentiment_data = {}
        self.theme_data = []
        self.word_frequency_data = []
        self.current_analysis_type = ""

    # UI update methods (called by service)
    def set_loading(self, loading: bool):
        """Set loading state"""
        self.is_loading = loading
        
        if loading and self.loading_overlay:
            self.add_widget(self.loading_overlay)
        elif self.loading_overlay in self.children:
            self.remove_widget(self.loading_overlay)

    def display_qualitative_results(self, results: Dict):
        """Display qualitative analysis results - called by service"""
        self.analysis_results = results
        
        if not self.qualitative_handler:
            return
        
        # Extract data for UI display
        self.text_analysis_summary = self.qualitative_handler.get_text_analysis_summary(results)
        
        # Extract text data if available
        text_data = None
        if 'analyses' in results and 'text' in results['analyses']:
            text_data = results['analyses']['text']
        elif 'text_analysis' in results:
            text_data = results['text_analysis']
        
        if text_data:
            self.text_results_data = self.qualitative_handler.get_text_results_data(text_data)
        
        # Update UI displays
        self.update_results_display()
        
        # Show success message
        toast("Qualitative analysis completed")

    def update_results_display(self):
        """Update results display in UI"""
        try:
            # Update main results display
            if hasattr(self.ids, 'results_content'):
                # This will be bound to properties in the KV file
                pass
            
            # Update status indicators
            if hasattr(self.ids, 'analysis_status_label'):
                if self.analysis_results:
                    self.ids.analysis_status_label.text = "Status: Analysis Complete"
                else:
                    self.ids.analysis_status_label.text = "Status: Ready"
                    
        except Exception as e:
            print(f"Error updating results display: {e}")

    def show_error(self, error_message: str):
        """Show error message"""
        toast(error_message)
        
        # Update error display in UI if needed
        if hasattr(self.ids, 'error_label'):
            self.ids.error_label.text = error_message

    def show_success(self, message: str):
        """Show success message"""
        toast(message)

    # Analysis type methods
    def show_analysis_type_dialog(self):
        """Show analysis type selection dialog"""
        # This will be handled by the .kv file dialog
        if hasattr(self.ids, 'analysis_type_dialog'):
            self.ids.analysis_type_dialog.open()

    def run_analysis_by_type(self, analysis_type: str):
        """Run analysis by type"""
        if analysis_type == "sentiment":
            self.run_sentiment_analysis()
        elif analysis_type == "theme":
            self.run_theme_analysis()
        elif analysis_type == "text":
            self.run_text_analysis()
        else:
            toast(f"Unknown analysis type: {analysis_type}")

    # Export methods
    def export_to_json(self):
        """Export results to JSON"""
        self.export_text_results()

    def export_to_csv(self):
        """Export results to CSV"""
        toast("CSV export coming soon")

    def share_results(self):
        """Share analysis results"""
        toast("Share functionality coming soon")

    # Utility methods
    def get_analysis_summary(self) -> str:
        """Get analysis summary text"""
        if not self.text_analysis_summary:
            return "No analysis completed yet"
        
        fields_count = self.text_analysis_summary.get('text_fields_analyzed', 0)
        total_entries = self.text_analysis_summary.get('total_text_entries', 'N/A')
        
        return f"Analyzed {fields_count} text fields with {total_entries} entries"

    def is_analysis_complete(self) -> bool:
        """Check if analysis is complete"""
        return bool(self.analysis_results and not self.is_loading)

    def has_text_results(self) -> bool:
        """Check if there are text analysis results available"""
        return bool(self.text_results_data.get('has_results', False))

    def has_sentiment_data(self) -> bool:
        """Check if there is sentiment data available"""
        return bool(self.sentiment_data)

    def has_theme_data(self) -> bool:
        """Check if there is theme data available"""
        return bool(self.theme_data)

    def has_word_frequency_data(self) -> bool:
        """Check if there is word frequency data available"""
        return bool(self.word_frequency_data) 