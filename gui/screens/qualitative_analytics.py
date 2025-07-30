from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.window import Window

from utils.cross_platform_toast import toast
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.card import MDCard

import json
import threading
import uuid
from typing import Dict, List, Any, Optional

from widgets.loading_overlay import LoadingOverlay
from services.qualitative_analytics import QualitativeAnalyticsHandler

class QualitativeOverviewCard(MDCard):
    """Custom card widget for displaying qualitative analysis overview"""
    text_fields_analyzed = StringProperty("0")
    total_text_entries = StringProperty("N/A")
    analyzed_fields_text = StringProperty("Fields: None")
    analysis_status = StringProperty("No analysis completed yet")

class QualitativeResultsCard(MDCard):
    """Custom card widget for displaying qualitative analysis results"""
    current_analysis_type = StringProperty("")

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
    
    # Computed properties for UI binding
    text_fields_analyzed = StringProperty("0")
    total_text_entries = StringProperty("N/A")
    analyzed_fields_text = StringProperty("")
    analysis_status = StringProperty("No analysis completed yet")
    
    # All analysis results
    text_results = ObjectProperty({})
    sentiment_results = ObjectProperty({})
    theme_results = ObjectProperty({})
    word_frequency_results = ObjectProperty({})
    content_analysis_results = ObjectProperty({})
    qualitative_coding_results = ObjectProperty({})
    survey_analysis_results = ObjectProperty({})
    qualitative_statistics_results = ObjectProperty({})
    sentiment_trends_results = ObjectProperty({})
    text_similarity_results = ObjectProperty({})
    theme_evolution_results = ObjectProperty({})
    quote_extraction_results = ObjectProperty({})
    
    # UI state
    selected_analysis_type = StringProperty("")
    selected_method = StringProperty("")
    text_fields = ListProperty([])
    selected_text_fields = ObjectProperty(set())
    
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
        
        # Initialize all result objects
        self.text_results = {}
        self.sentiment_results = {}
        self.theme_results = {}
        self.word_frequency_results = {}
        self.content_analysis_results = {}
        self.qualitative_coding_results = {}
        self.survey_analysis_results = {}
        self.qualitative_statistics_results = {}
        self.sentiment_trends_results = {}
        self.text_similarity_results = {}
        self.theme_evolution_results = {}
        self.quote_extraction_results = {}
        
        # Bind property updates
        self.bind(text_analysis_summary=self.update_computed_properties)
        self.bind(current_analysis_type=self.update_results_card)
        
        # Initialize UI state
        self.selected_analysis_type = ""
        self.selected_method = ""
        self.text_fields = []
        self.selected_text_fields = set()
        
        # Initialize loading overlay
        self.loading_overlay = LoadingOverlay()
        
        # Bind to window resize for responsive updates
        Window.bind(size=self.on_window_resize)

    def update_computed_properties(self, instance, value):
        """Update computed properties when text_analysis_summary changes"""
        if not value:
            text_fields_analyzed = "0"
            total_text_entries = "N/A"
            analyzed_fields_text = "Fields: None"
            analysis_status = "No analysis completed yet"
        else:
            text_fields_analyzed = str(value.get('text_fields_analyzed', 0))
            total_text_entries = str(value.get('total_text_entries', 'N/A'))
            
            fields = value.get('fields', [])
            has_more = value.get('has_more_fields', False)
            if fields:
                fields_text = ', '.join(fields)
                if has_more:
                    fields_text += '...'
                analyzed_fields_text = f"Fields: {fields_text}"
            else:
                analyzed_fields_text = "Fields: None"
            
            analysis_status = value.get('status', 'Analysis completed')
        
        # Update screen properties
        self.text_fields_analyzed = text_fields_analyzed
        self.total_text_entries = total_text_entries
        self.analyzed_fields_text = analyzed_fields_text
        self.analysis_status = analysis_status
        
        # Update overview card if it exists
        if hasattr(self.ids, 'overview_card') and self.ids.overview_card:
            self.ids.overview_card.text_fields_analyzed = text_fields_analyzed
            self.ids.overview_card.total_text_entries = total_text_entries
            self.ids.overview_card.analyzed_fields_text = analyzed_fields_text
            self.ids.overview_card.analysis_status = analysis_status
        
        # Update results card if it exists
        if hasattr(self.ids, 'results_card') and self.ids.results_card:
            self.ids.results_card.current_analysis_type = self.current_analysis_type

    def update_results_card(self, instance, value):
        """Update results card when current_analysis_type changes"""
        if hasattr(self.ids, 'results_card') and self.ids.results_card:
            self.ids.results_card.current_analysis_type = value

    def on_enter(self):
        """Called when the screen is entered"""
        if hasattr(self.ids, 'top_bar') and self.ids.top_bar:
            self.ids.top_bar.set_title("Qualitative Analytics")
            self.ids.top_bar.set_current_screen("qualitative_analytics")
        
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
        
        # Load project text fields
        self.load_project_text_fields(project_id)

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

    def load_project_text_fields(self, project_id: str):
        """Load text fields for the selected project"""
        try:
            if self.analytics_service:
                variables = self.analytics_service.get_project_variables(project_id)
                self.text_fields = variables.get('text_variables', [])
        except Exception as e:
            print(f"Error loading text fields: {e}")
    
    def toggle_text_field_selection(self, field: str, selected: bool):
        """Toggle text field selection"""
        if selected:
            self.selected_text_fields.add(field)
        else:
            self.selected_text_fields.discard(field)
    
    # NEW COMPREHENSIVE ANALYSIS METHODS
    
    def run_sentiment_analysis_full(self, config: Dict = None):
        """Run comprehensive sentiment analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        if not config:
            config = {
                'text_fields': list(self.selected_text_fields) if self.selected_text_fields else None,
                'sentiment_method': self.selected_method or 'vader'
            }
        
        self.qualitative_handler.run_sentiment_analysis_full(self.current_project_id, config)
    
    def run_theme_analysis_full(self, config: Dict = None):
        """Run comprehensive theme analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        if not config:
            config = {
                'text_fields': list(self.selected_text_fields) if self.selected_text_fields else None,
                'num_themes': 5,
                'theme_method': self.selected_method or 'lda'
            }
        
        self.qualitative_handler.run_theme_analysis_full(self.current_project_id, config)
    
    def run_word_frequency_analysis(self, config: Dict = None):
        """Run word frequency analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        if not config:
            config = {
                'text_fields': list(self.selected_text_fields) if self.selected_text_fields else None,
                'top_n': 50,
                'min_word_length': 3,
                'remove_stopwords': True
            }
        
        self.qualitative_handler.run_word_frequency_analysis(self.current_project_id, config)
    
    def run_content_analysis(self, config: Dict = None):
        """Run content analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        if not config:
            config = {
                'text_fields': list(self.selected_text_fields) if self.selected_text_fields else None,
                'analysis_framework': self.selected_method or 'inductive'
            }
        
        self.qualitative_handler.run_content_analysis(self.current_project_id, config)
    
    def run_qualitative_coding(self, config: Dict = None):
        """Run qualitative coding"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        if not config:
            config = {
                'text_fields': list(self.selected_text_fields) if self.selected_text_fields else None,
                'coding_method': self.selected_method or 'open',
                'auto_code': True
            }
        
        self.qualitative_handler.run_qualitative_coding(self.current_project_id, config)
    
    def run_survey_analysis(self, config: Dict = None):
        """Run survey analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        if not config:
            config = {
                'response_fields': list(self.selected_text_fields) if self.selected_text_fields else None
            }
        
        self.qualitative_handler.run_survey_analysis(self.current_project_id, config)
    
    def run_qualitative_statistics(self, config: Dict = None):
        """Run qualitative statistics"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        if not config:
            config = {
                'text_fields': list(self.selected_text_fields) if self.selected_text_fields else None,
                'analysis_type': self.selected_method or 'general'
            }
        
        self.qualitative_handler.run_qualitative_statistics(self.current_project_id, config)
    
    def run_sentiment_trends(self, config: Dict = None):
        """Run sentiment trends analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        if not config:
            config = {
                'text_fields': list(self.selected_text_fields) if self.selected_text_fields else None,
                'sentiment_method': 'vader'
            }
        
        self.qualitative_handler.run_sentiment_trends(self.current_project_id, config)
    
    def run_text_similarity(self, config: Dict = None):
        """Run text similarity analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        if not config:
            config = {
                'text_fields': list(self.selected_text_fields) if self.selected_text_fields else None,
                'similarity_threshold': 0.5,
                'max_comparisons': 100
            }
        
        self.qualitative_handler.run_text_similarity(self.current_project_id, config)
    
    def run_theme_evolution(self, config: Dict = None):
        """Run theme evolution analysis"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        if not config:
            config = {
                'text_fields': list(self.selected_text_fields) if self.selected_text_fields else None,
                'num_themes': 5
            }
        
        self.qualitative_handler.run_theme_evolution(self.current_project_id, config)
    
    def run_quote_extraction(self, config: Dict = None):
        """Run quote extraction"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.qualitative_handler:
            toast("Qualitative analytics service not available")
            return
        
        if not config:
            config = {
                'text_fields': list(self.selected_text_fields) if self.selected_text_fields else None,
                'max_quotes': 5,
                'auto_extract_themes': True
            }
        
        self.qualitative_handler.run_quote_extraction(self.current_project_id, config)

    def clear_results(self):
        """Clear all analysis results and reset state"""
        self.analysis_results = {}
        self.text_analysis_summary = {}
        self.text_results_data = {}
        self.sentiment_data = {}
        self.theme_data = []
        self.word_frequency_data = []
        self.current_analysis_type = ""
        
        # Clear all new result objects
        self.text_results = {}
        self.sentiment_results = {}
        self.theme_results = {}
        self.word_frequency_results = {}
        self.content_analysis_results = {}
        self.qualitative_coding_results = {}
        self.survey_analysis_results = {}
        self.qualitative_statistics_results = {}
        self.sentiment_trends_results = {}
        self.text_similarity_results = {}
        self.theme_evolution_results = {}
        self.quote_extraction_results = {}
        
        # Reset UI state
        self.selected_analysis_type = ""
        self.selected_method = ""
        self.selected_text_fields = set()

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
    
    def show_analysis_type_menu(self):
        """Show analysis type dropdown menu"""
        if not hasattr(self, 'analysis_type_menu') or not self.analysis_type_menu:
            from kivymd.uix.menu import MDDropdownMenu
            
            analysis_types = self.get_available_analysis_types()
            menu_items = []
            
            for analysis_type in analysis_types:
                menu_items.append({
                    "text": analysis_type['name'],
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=analysis_type['id']: self.select_analysis_type(x),
                })
                
            self.analysis_type_menu = MDDropdownMenu(
                items=menu_items,
                width_mult=4,
                max_height=dp(300)
            )
        
        if hasattr(self.ids, 'analysis_type_button'):
            self.analysis_type_menu.caller = self.ids.analysis_type_button
            self.analysis_type_menu.open()
    
    def show_analysis_method_menu(self):
        """Show analysis method dropdown menu"""
        if not self.selected_analysis_type:
            toast("Please select an analysis type first")
            return
        
        methods = self.get_analysis_methods(self.selected_analysis_type)
        if not methods:
            toast("No methods available for this analysis type")
            return
        
        from kivymd.uix.menu import MDDropdownMenu
        
        menu_items = []
        for method in methods:
            menu_items.append({
                "text": method.replace('_', ' ').title(),
                "viewclass": "OneLineListItem", 
                "on_release": lambda x=method: self.select_analysis_method(x),
            })
            
        method_menu = MDDropdownMenu(
            items=menu_items,
            width_mult=4,
            max_height=dp(200)
        )
        
        if hasattr(self.ids, 'analysis_method_button'):
            method_menu.caller = self.ids.analysis_method_button
            method_menu.open()

    def run_analysis_by_type(self, analysis_type: str):
        """Run analysis by type"""
        self.selected_analysis_type = analysis_type
        
        if analysis_type == "text":
            self.run_text_analysis()
        elif analysis_type == "sentiment":
            self.run_sentiment_analysis_full()
        elif analysis_type == "themes":
            self.run_theme_analysis_full()
        elif analysis_type == "word_frequency":
            self.run_word_frequency_analysis()
        elif analysis_type == "content_analysis":
            self.run_content_analysis()
        elif analysis_type == "qualitative_coding":
            self.run_qualitative_coding()
        elif analysis_type == "survey_analysis":
            self.run_survey_analysis()
        elif analysis_type == "qualitative_statistics":
            self.run_qualitative_statistics()
        elif analysis_type == "sentiment_trends":
            self.run_sentiment_trends()
        elif analysis_type == "text_similarity":
            self.run_text_similarity()
        elif analysis_type == "theme_evolution":
            self.run_theme_evolution()
        elif analysis_type == "quote_extraction":
            self.run_quote_extraction()
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
    
    # NEW HELPER METHODS FOR ALL ANALYSIS TYPES
    
    def get_available_analysis_types(self) -> List[Dict]:
        """Get all available analysis types"""
        if self.qualitative_handler:
            return self.qualitative_handler.get_analysis_types()
        return []
    
    def get_analysis_methods(self, analysis_type: str) -> List[str]:
        """Get available methods for analysis type"""
        if self.qualitative_handler:
            return self.qualitative_handler.get_analysis_methods(analysis_type)
        return []
    
    def select_analysis_type(self, analysis_type: str):
        """Select analysis type and update UI"""
        self.selected_analysis_type = analysis_type
        # Update methods dropdown based on selected type
        methods = self.get_analysis_methods(analysis_type)
        if methods:
            self.selected_method = methods[0]  # Select first method by default
    
    def select_analysis_method(self, method: str):
        """Select analysis method"""
        self.selected_method = method
    
    def switch_results_tab(self, tab_name: str):
        """Switch between result tabs"""
        # This will be handled by the KV file to show/hide different result displays
        pass
    
    def get_current_results(self):
        """Get current analysis results based on type"""
        results_map = {
            'text': self.text_results,
            'sentiment': self.sentiment_results,
            'themes': self.theme_results,
            'word_frequency': self.word_frequency_results,
            'content_analysis': self.content_analysis_results,
            'qualitative_coding': self.qualitative_coding_results,
            'survey_analysis': self.survey_analysis_results,
            'qualitative_statistics': self.qualitative_statistics_results,
            'sentiment_trends': self.sentiment_trends_results,
            'text_similarity': self.text_similarity_results,
            'theme_evolution': self.theme_evolution_results,
            'quote_extraction': self.quote_extraction_results
        }
        
        return results_map.get(self.current_analysis_type, {})
    
    def has_results(self, analysis_type: str = None) -> bool:
        """Check if there are results for specific analysis type"""
        if not analysis_type:
            analysis_type = self.current_analysis_type
        
        results_map = {
            'text': bool(self.text_results),
            'sentiment': bool(self.sentiment_results),
            'themes': bool(self.theme_results),
            'word_frequency': bool(self.word_frequency_results),
            'content_analysis': bool(self.content_analysis_results),
            'qualitative_coding': bool(self.qualitative_coding_results),
            'survey_analysis': bool(self.survey_analysis_results),
            'qualitative_statistics': bool(self.qualitative_statistics_results),
            'sentiment_trends': bool(self.sentiment_trends_results),
            'text_similarity': bool(self.text_similarity_results),
            'theme_evolution': bool(self.theme_evolution_results),
            'quote_extraction': bool(self.quote_extraction_results)
        }
        
        return results_map.get(analysis_type, False) 