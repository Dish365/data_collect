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
from services.data_exploration_service import DataExplorationService

Builder.load_file("kv/data_exploration.kv")

class DataExplorationScreen(Screen):
    """Data Exploration Screen - handles UI interactions and delegates logic to service"""
    
    # Screen properties
    current_project_id = StringProperty(None, allownone=True)
    current_project_name = StringProperty("")
    project_list = ListProperty([])
    project_map = {}
    
    # Data state
    current_data = ListProperty([])
    selected_responses = ObjectProperty(set())
    current_page = 1
    page_size = 50
    total_count = 0
    total_pages = 0
    
    # Filter state
    current_filters = ObjectProperty({})
    filter_options = ObjectProperty({})
    project_questions = ListProperty([])
    sample_size = 50
    
    # UI state
    is_loading = BooleanProperty(False)
    
    # UI references
    project_menu = None
    question_menu = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        
        # Initialize services
        self.auth_service = getattr(app, 'auth_service', None)
        self.analytics_service = getattr(app, 'analytics_service', None)
        
        # Initialize data exploration service
        if self.analytics_service:
            self.data_exploration_service = DataExplorationService(
                self.analytics_service, self
            )
        else:
            print("Warning: Analytics service not available")
            self.data_exploration_service = None
        
        # Initialize state
        self.selected_responses = set()
        self.current_filters = {}
        self.filter_options = {}
        
        # Initialize loading overlay
        self.loading_overlay = LoadingOverlay()
        
        # Bind to window resize for responsive updates
        Window.bind(size=self.on_window_resize)

    def on_enter(self):
        """Called when the screen is entered"""
        if hasattr(self.ids, 'top_bar') and self.ids.top_bar:
            self.ids.top_bar.set_title("Data Exploration")
            self.ids.top_bar.set_current_screen("data_exploration")
        
        # Initialize responsive layout
        self.update_responsive_layout()
        
        # Load projects for selection
        self.load_projects()

    def on_window_resize(self, window, size):
        """Handle window resize for responsive layout adjustments"""
        try:
            Clock.schedule_once(lambda dt: self.update_responsive_layout(), 0.1)
        except Exception as e:
            print(f"Error handling window resize in data exploration: {e}")

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
        """Select a project and start data exploration"""
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
        
        # Start data exploration
        self.start_data_exploration()

    def start_data_exploration(self):
        """Start data exploration for selected project"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        
        if not self.data_exploration_service:
            toast("Data exploration service not available")
            return
        
        # Delegate to service
        self.data_exploration_service.explore_project_data(self.current_project_id)

    # Filter methods
    def apply_filters(self):
        """Apply current filters"""
        if not self.data_exploration_service:
            return
        
        self.data_exploration_service.apply_filters(self.current_project_id)

    def clear_filters(self):
        """Clear all filters"""
        if not self.data_exploration_service:
            return
        
        self.data_exploration_service.clear_filters(self.current_project_id)

    def show_question_filter_menu(self):
        """Show question filter menu"""
        if not self.data_exploration_service:
            return
        
        self.data_exploration_service.show_question_filter_menu(self.current_project_id)

    # Pagination methods
    def load_previous_page(self):
        """Load previous page of data"""
        if not self.data_exploration_service:
            return
        
        self.data_exploration_service.load_previous_page(self.current_project_id)

    def load_next_page(self):
        """Load next page of data"""
        if not self.data_exploration_service:
            return
        
        self.data_exploration_service.load_next_page(self.current_project_id)

    # Selection methods
    def sample_random(self):
        """Sample random responses"""
        if not self.data_exploration_service:
            return
        
        self.data_exploration_service.sample_random(self.current_project_id)

    def sample_first_n(self):
        """Sample first N responses"""
        if not self.data_exploration_service:
            return
        
        self.data_exploration_service.sample_first_n(self.current_project_id)

    def sample_latest_n(self):
        """Sample latest N responses"""
        if not self.data_exploration_service:
            return
        
        self.data_exploration_service.sample_latest_n(self.current_project_id)

    def sample_high_quality(self):
        """Sample high quality responses"""
        if not self.data_exploration_service:
            return
        
        self.data_exploration_service.sample_high_quality(self.current_project_id)

    def select_all_responses(self):
        """Select all responses with current filters"""
        if not self.data_exploration_service:
            return
        
        self.data_exploration_service.select_all_responses(self.current_project_id)

    def clear_selection(self):
        """Clear response selection"""
        if not self.data_exploration_service:
            return
        
        self.data_exploration_service.clear_selection()

    def export_selected_responses(self):
        """Export selected responses"""
        if not self.data_exploration_service:
            return
        
        self.data_exploration_service.export_selected_responses()

    def toggle_response_selection(self, response_id: str, active: bool):
        """Toggle individual response selection"""
        if not self.data_exploration_service:
            return
        
        self.data_exploration_service.toggle_response_selection(response_id, active)

    def toggle_page_selection(self, active: bool):
        """Toggle all responses on current page"""
        if not self.data_exploration_service:
            return
        
        self.data_exploration_service.toggle_page_selection(active)

    # UI update methods (called by service)
    def set_loading(self, loading: bool):
        """Set loading state"""
        self.is_loading = loading
        
        if loading and self.loading_overlay:
            self.add_widget(self.loading_overlay)
        elif self.loading_overlay in self.children:
            self.remove_widget(self.loading_overlay)

    def update_data_display(self, data: List[Dict], pagination: Dict):
        """Update data display - called by service"""
        self.current_data = data
        
        # Update pagination info
        self.total_count = pagination.get('total_count', 0)
        self.total_pages = pagination.get('total_pages', 0)
        
        # Update UI elements through IDs
        self._update_data_table()
        self._update_pagination_info()

    def update_filter_status(self, filters_applied: List[str]):
        """Update filter status indicators"""
        try:
            if hasattr(self.ids, 'filter_status_label'):
                if filters_applied:
                    self.ids.filter_status_label.text = f"{len(filters_applied)} active"
                else:
                    self.ids.filter_status_label.text = ""
            
            if hasattr(self.ids, 'filter_summary_label'):
                if filters_applied:
                    self.ids.filter_summary_label.text = "Active filters: " + " • ".join(filters_applied)
                else:
                    self.ids.filter_summary_label.text = ""
                    
        except Exception as e:
            print(f"Error updating filter status: {e}")

    def update_selection_info(self, selection_count: int):
        """Update selection information"""
        try:
            if hasattr(self.ids, 'selection_info_label'):
                if selection_count == 0:
                    self.ids.selection_info_label.text = "No responses selected"
                elif selection_count == 1:
                    self.ids.selection_info_label.text = "1 response selected"
                else:
                    self.ids.selection_info_label.text = f"{selection_count:,} responses selected"
        except Exception as e:
            print(f"Error updating selection info: {e}")

    def _update_data_table(self):
        """Update data table display"""
        # This will be handled by the KV file binding to current_data property
        pass

    def _update_pagination_info(self):
        """Update pagination information"""
        try:
            if hasattr(self.ids, 'page_info_label'):
                if self.total_count > 0:
                    start_record = ((self.current_page - 1) * self.page_size) + 1
                    end_record = min(self.current_page * self.page_size, self.total_count)
                    self.ids.page_info_label.text = f"Page {self.current_page}/{self.total_pages} • {start_record}-{end_record} of {self.total_count:,}"
                else:
                    self.ids.page_info_label.text = "No records found"
            
            # Update button states
            if hasattr(self.ids, 'prev_btn'):
                self.ids.prev_btn.disabled = self.current_page <= 1
            if hasattr(self.ids, 'next_btn'):
                self.ids.next_btn.disabled = self.current_page >= self.total_pages
                
        except Exception as e:
            print(f"Error updating pagination info: {e}")

    def show_error(self, error_message: str):
        """Show error message"""
        toast(error_message)
        
        # Update error display in UI if needed
        if hasattr(self.ids, 'error_label'):
            self.ids.error_label.text = error_message

    def get_sample_size(self) -> int:
        """Get sample size from UI input"""
        try:
            if hasattr(self.ids, 'sample_size_field') and self.ids.sample_size_field.text:
                return int(self.ids.sample_size_field.text)
            return self.sample_size
        except ValueError:
            return self.sample_size

    def get_search_text(self) -> str:
        """Get search text from UI input"""
        if hasattr(self.ids, 'search_field'):
            return self.ids.search_field.text
        return ""

    def get_respondent_filter(self) -> str:
        """Get respondent filter from UI input"""
        if hasattr(self.ids, 'respondent_field'):
            return self.ids.respondent_field.text
        return "" 