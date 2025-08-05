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

# KV file loaded by main app after theme initialization

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

    def find_widget_by_id(self, parent_widget, widget_id):
        """Helper method to find a widget by ID within a parent widget"""
        if hasattr(parent_widget, 'ids') and widget_id in parent_widget.ids:
            return parent_widget.ids[widget_id]
        
        # Search recursively through children
        for child in parent_widget.children:
            if hasattr(child, 'ids') and widget_id in child.ids:
                return child.ids[widget_id]
            result = self.find_widget_by_id(child, widget_id)
            if result:
                return result
        return None

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
            app = App.get_running_app()
            if not hasattr(app, 'db_service') or not app.db_service:
                toast("Database service not available")
                return
            
            def load_projects_thread():
                try:
                    conn = app.db_service.get_db_connection()
                    if conn is None:
                        Clock.schedule_once(
                            lambda dt: toast("Database not initialized"), 0.1
                        )
                        return
                    
                    cursor = conn.cursor()
                    user_data = app.auth_service.get_user_data() if app.auth_service else None
                    user_id = user_data.get('id') if user_data else None
                    
                    if user_id:
                        cursor.execute("""
                            SELECT id, name, description, created_at,
                                   (SELECT COUNT(*) FROM responses WHERE project_id = projects.id) as response_count
                            FROM projects 
                            WHERE user_id = ? 
                            ORDER BY name
                        """, (user_id,))
                    else:
                        cursor.execute("""
                            SELECT id, name, description, created_at,
                                   (SELECT COUNT(*) FROM responses WHERE project_id = projects.id) as response_count
                            FROM projects 
                            ORDER BY name
                        """)
                    
                    projects = cursor.fetchall()
                    conn.close()
                    
                    # Convert to list of dictionaries
                    project_list = [
                        {
                            'id': p['id'],
                            'name': p['name'],
                            'description': p['description'] or '',
                            'response_count': p['response_count'] or 0,
                            'created_at': p['created_at']
                        }
                        for p in projects
                    ]
                    
                    Clock.schedule_once(
                        lambda dt: self._handle_projects_loaded(project_list), 0.1
                    )
                    
                except Exception as e:
                    error_msg = str(e)  # Capture the error message in local scope
                    Clock.schedule_once(
                        lambda dt: toast(f"Failed to load projects: {error_msg}"), 0.1
                    )
                finally:
                    if 'conn' in locals() and conn:
                        conn.close()
            
            threading.Thread(target=load_projects_thread, daemon=True).start()
            
        except Exception as e:
            toast(f"Error loading projects: {str(e)}")

    def _handle_projects_loaded(self, projects):
        """Handle loaded projects"""
        try:
            self.project_list = projects  # Store full project objects
            self.project_map = {}
            
            # Create name-to-id mapping for compatibility
            for project in projects:
                project_name = project.get('name', 'Unnamed Project')
                project_id = project.get('id', '')
                self.project_map[project_name] = project_id
            
            # Update project selector UI
            project_selector = self.find_widget_by_id(self.ids.project_selection_card, 'project_selector') if hasattr(self.ids, 'project_selection_card') else None
            if project_selector:
                if self.project_list:
                    project_selector.text = "Select Project"
                else:
                    project_selector.text = "No Projects Available"
            
            # Update project info label
            project_info_label = self.find_widget_by_id(self.ids.project_selection_card, 'project_info_label') if hasattr(self.ids, 'project_selection_card') else None
            if project_info_label:
                if self.project_list:
                    total_projects = len(self.project_list)
                    total_responses = sum(p.get('response_count', 0) for p in self.project_list)
                    project_info_label.text = f"{total_projects} projects • {total_responses} responses"
                else:
                    project_info_label.text = "No projects found"
                    
        except Exception as e:
            toast(f"Error processing projects: {str(e)}")

    def show_project_menu(self):
        """Show project selection menu"""
        if not self.project_list:
            toast("No projects available")
            return
        
        # Import the two-line menu item class
        from widgets.two_line_menu_item import TwoLineMenuItem
        
        menu_items = []
        for project in self.project_list:
            # Create separate headline and supporting text
            headline_text = project['name']
            supporting_text = f"{project['response_count']} responses"
            if project.get('description'):
                supporting_text += f" • {project['description'][:30]}{'...' if len(project['description']) > 30 else ''}"
            
            menu_items.append({
                "headline": headline_text,
                "supporting": supporting_text,
                "viewclass": "TwoLineMenuItem",
                "height": dp(72),
                "on_release": lambda x=project: self.select_project(x)
            })
        
        project_selector = self.find_widget_by_id(self.ids.project_selection_card, 'project_selector') if hasattr(self.ids, 'project_selection_card') else None
        if not project_selector:
            toast("Project selector not found")
            return
            
        self.project_menu = MDDropdownMenu(
            caller=project_selector,
            items=menu_items,
            width=dp(280),
            max_height=dp(400)
        )
        self.project_menu.open()

    def select_project(self, project):
        """Select a project and start data exploration"""
        if hasattr(self, 'project_menu') and self.project_menu:
            self.project_menu.dismiss()
        
        # Handle both old string format and new project object format
        if isinstance(project, str):
            # Legacy format - project name only
            project_id = self.project_map.get(project)
            project_name = project
            if not project_id:
                toast("Invalid project selection")
                return
        else:
            # New format - full project object
            project_id = project.get('id')
            project_name = project.get('name')
            if not project_id or not project_name:
                toast("Invalid project data")
                return
        
        self.current_project_id = project_id
        self.current_project_name = project_name
        
        # Update UI
        project_selector = self.find_widget_by_id(self.ids.project_selection_card, 'project_selector') if hasattr(self.ids, 'project_selection_card') else None
        if project_selector:
            if isinstance(project, dict) and project.get('response_count', 0) > 0:
                project_selector.text = f"{project_name} ({project['response_count']} responses)"
            else:
                project_selector.text = project_name
        
        # Update project info
        project_info_label = self.find_widget_by_id(self.ids.project_selection_card, 'project_info_label') if hasattr(self.ids, 'project_selection_card') else None
        if project_info_label:
            if isinstance(project, dict):
                response_count = project.get('response_count', 0)
                project_info_label.text = f"Selected • {response_count} responses"
            else:
                project_info_label.text = "Selected"
        
        toast(f"Selected project: {project_name}")
        
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
            filter_status_label = self.find_widget_by_id(self.ids.filters_card, 'filter_status_label') if hasattr(self.ids, 'filters_card') else None
            if filter_status_label:
                if filters_applied:
                    filter_status_label.text = f"{len(filters_applied)} active"
                else:
                    filter_status_label.text = ""
            
            filter_summary_label = self.find_widget_by_id(self.ids.filters_card, 'filter_summary_label') if hasattr(self.ids, 'filters_card') else None
            if filter_summary_label:
                if filters_applied:
                    filter_summary_label.text = "Active filters: " + " • ".join(filters_applied)
                else:
                    filter_summary_label.text = ""
                    
        except Exception as e:
            print(f"Error updating filter status: {e}")

    def update_selection_info(self, selection_count: int):
        """Update selection information"""
        try:
            selection_info_label = self.find_widget_by_id(self.ids.selection_card, 'selection_info_label') if hasattr(self.ids, 'selection_card') else None
            if selection_info_label:
                if selection_count == 0:
                    selection_info_label.text = "No responses selected"
                elif selection_count == 1:
                    selection_info_label.text = "1 response selected"
                else:
                    selection_info_label.text = f"{selection_count:,} responses selected"
        except Exception as e:
            print(f"Error updating selection info: {e}")

    def _update_data_table(self):
        """Update data table display"""
        # This will be handled by the KV file binding to current_data property
        pass

    def _update_pagination_info(self):
        """Update pagination information"""
        try:
            page_info_label = self.find_widget_by_id(self.ids.preview_card, 'page_info_label') if hasattr(self.ids, 'preview_card') else None
            if page_info_label:
                if self.total_count > 0:
                    start_record = ((self.current_page - 1) * self.page_size) + 1
                    end_record = min(self.current_page * self.page_size, self.total_count)
                    page_info_label.text = f"Page {self.current_page}/{self.total_pages} • {start_record}-{end_record} of {self.total_count:,}"
                else:
                    page_info_label.text = "No records found"
            
            # Update button states
            prev_btn = self.find_widget_by_id(self.ids.preview_card, 'prev_btn') if hasattr(self.ids, 'preview_card') else None
            if prev_btn:
                prev_btn.disabled = self.current_page <= 1
                
            next_btn = self.find_widget_by_id(self.ids.preview_card, 'next_btn') if hasattr(self.ids, 'preview_card') else None
            if next_btn:
                next_btn.disabled = self.current_page >= self.total_pages
                
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
            sample_size_field = self.find_widget_by_id(self.ids.selection_card, 'sample_size_field') if hasattr(self.ids, 'selection_card') else None
            if sample_size_field and sample_size_field.text:
                return int(sample_size_field.text)
            return self.sample_size
        except ValueError:
            return self.sample_size

    def get_search_text(self) -> str:
        """Get search text from UI input"""
        search_field = self.find_widget_by_id(self.ids.filters_card, 'search_field') if hasattr(self.ids, 'filters_card') else None
        if search_field:
            return search_field.text
        return ""

    def get_respondent_filter(self) -> str:
        """Get respondent filter from UI input"""
        respondent_field = self.find_widget_by_id(self.ids.filters_card, 'respondent_field') if hasattr(self.ids, 'filters_card') else None
        if respondent_field:
            return respondent_field.text
        return ""
    
    # Navigation methods
    def navigate_to_analytics_hub(self):
        """Navigate back to analytics hub"""
        app = App.get_running_app()
        app.root.current = 'analytics'
        toast("Returning to Analytics Hub...")
    
    def navigate_to_descriptive_analytics(self):
        """Navigate to descriptive analytics"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        self._navigate_with_project_data('descriptive_analytics', 'Descriptive Analytics')
    
    def navigate_to_qualitative_analytics(self):
        """Navigate to qualitative analytics"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        self._navigate_with_project_data('qualitative_analytics', 'Qualitative Analytics')
    
    def navigate_to_inferential_analytics(self):
        """Navigate to inferential analytics"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        self._navigate_with_project_data('inferential_analytics', 'Inferential Analytics')
    
    def navigate_to_auto_detection(self):
        """Navigate to auto detection"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        self._navigate_with_project_data('auto_detection', 'Auto Detection')
    
    def _navigate_with_project_data(self, screen_name: str, display_name: str):
        """Navigate to another screen while passing current project data"""
        try:
            app = App.get_running_app()
            
            # Get target screen and pass project data
            if hasattr(app.root, 'get_screen'):
                target_screen = app.root.get_screen(screen_name)
                if hasattr(target_screen, 'current_project_id'):
                    target_screen.current_project_id = self.current_project_id
                if hasattr(target_screen, 'current_project_name'):
                    target_screen.current_project_name = self.current_project_name
                if hasattr(target_screen, 'analytics_service'):
                    target_screen.analytics_service = self.analytics_service
            
            app.root.current = screen_name
            toast(f"Opening {display_name}...")
            
        except Exception as e:
            print(f"Error navigating to {screen_name}: {e}")
            toast(f"Could not navigate to {display_name}")
    
    def set_project_from_analytics_hub(self, project_id: str, project_name: str):
        """Set project when navigating from analytics hub"""
        self.current_project_id = project_id
        self.current_project_name = project_name
        
        # Update UI
        project_selector = self.find_widget_by_id(self.ids.project_selection_card, 'project_selector') if hasattr(self.ids, 'project_selection_card') else None
        if project_selector:
            project_selector.text = project_name
            
        # Start data exploration automatically
        Clock.schedule_once(lambda dt: self.start_data_exploration(), 0.1) 