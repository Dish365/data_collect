from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
from utils.cross_platform_toast import toast
from kivy.core.window import Window
from widgets.top_bar import TopBar
from kivymd.uix.menu import MDDropdownMenu

import threading
from datetime import datetime
from typing import Dict, List

#:kivy 2.0

Builder.load_file('kv/analytics.kv')

class AnalyticsScreen(Screen):
    """Analytics Screen - Navigation hub for analytics features"""
    
    # Properties
    current_project_id = StringProperty(None, allownone=True)
    current_project_name = StringProperty("")
    project_list = ListProperty([])
    project_map = {}
    
    # UI state
    is_project_overview_collapsed = BooleanProperty(False)
    
    # UI references
    project_menu = None
    analytics_service = None
    
    # UI constants
    CARD_HEIGHT = dp(200)
    PADDING = dp(24)
    SPACING = dp(20)
    BUTTON_HEIGHT = dp(48)
    ICON_SIZE = dp(32)
    FONT_SIZE = "16sp"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.on_window_resize)

    def _detect_tablet(self):
        """Detect if we're running on a tablet-sized device"""
        width = Window.width
        return 768 <= width <= 1366



    def on_enter(self):
        """Initialize analytics screen when entered"""
        Clock.schedule_once(self._delayed_init, 0.1)

    def _delayed_init(self, dt):
        """Delayed initialization"""
        if hasattr(self.ids, 'top_bar'):
            self.ids.top_bar.set_title("Analytics Hub")
            self.ids.top_bar.set_current_screen('analytics')
        
        self.setup_analytics_service()
        self.load_projects()
        self.update_responsive_layout()
        self.update_quick_stats()
        self.update_project_overview_collapse_state()

    def setup_analytics_service(self):
        """Initialize basic analytics service"""
        app = App.get_running_app()
        if not self.analytics_service:
            from services.analytics_service import AnalyticsService
            self.analytics_service = AnalyticsService(
                app.auth_service,
                app.db_service
            )

    def load_projects(self):
        """Load available projects"""
        try:
            app = App.get_running_app()
            conn = app.db_service.get_db_connection()
            
            if conn is None:
                toast("Database not initialized")
                return
                
            cursor = conn.cursor()
            user_data = app.auth_service.get_user_data()
            user_id = user_data.get('id') if user_data else None
            
            if user_id:
                cursor.execute("""
                    SELECT id, name, description, created_at,
                           (SELECT COUNT(*) FROM responses WHERE project_id = projects.id) as response_count,
                           (SELECT COUNT(DISTINCT respondent_id) FROM responses WHERE project_id = projects.id) as respondent_count
                    FROM projects 
                    WHERE user_id = ? 
                    ORDER BY name
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT id, name, description, created_at,
                           (SELECT COUNT(*) FROM responses WHERE project_id = projects.id) as response_count,
                           (SELECT COUNT(DISTINCT respondent_id) FROM responses WHERE project_id = projects.id) as respondent_count
                    FROM projects 
                    ORDER BY name
                """)
                
            projects = cursor.fetchall()
            
            if not projects:
                toast("No projects available. Create a project first.")
                return
                
            self.project_list = [
                {
                    'id': p['id'],
                    'name': p['name'],
                    'description': p['description'] or '',
                    'response_count': p['response_count'] or 0,
                    'respondent_count': p['respondent_count'] or 0,
                    'created_at': p['created_at']
                }
                for p in projects
            ]
            
            self.project_map = {p['name']: p['id'] for p in projects}
            
            if hasattr(self.ids, 'project_selector'):
                self.ids.project_selector.text = "Select Project for Analysis"
                self.ids.project_selector.font_size = self.FONT_SIZE
                
        except Exception as e:
            print(f"Error loading projects: {e}")
            toast("Error loading projects")
        finally:
            if conn:
                conn.close()



    def open_project_menu(self):
        """Open project selection dropdown menu"""
        if self.project_menu:
            self.project_menu.dismiss()
            
        if not self.project_list:
            toast("No projects available")
            return
            
        menu_items = []
        for project in self.project_list:
            item_text = f"{project['name']}\n" + \
                       f"{project['response_count']} responses • " + \
                       f"{project['respondent_count']} respondents"
            
            menu_items.append({
                "text": item_text,
                "viewclass": "TwoLineMenuItem",
                "height": dp(72),
                "font_size": self.FONT_SIZE,
                "on_release": lambda x=project: self.select_project(x)
            })
            
        self.project_menu = MDDropdownMenu(
            caller=self.ids.project_selector,
            items=menu_items,
            width_mult=5,
            max_height=dp(400)
        )
        self.project_menu.open()

    def select_project(self, project):
        """Select a project"""
        if self.project_menu:
            self.project_menu.dismiss()
            
        self.current_project_id = project['id']
        self.current_project_name = project['name']
        
        if hasattr(self.ids, 'project_selector'):
            selector_text = f"{project['name']}"
            if project['response_count'] > 0:
                selector_text += f" ({project['response_count']} responses)"
            self.ids.project_selector.text = selector_text
        
        self.update_quick_stats()
        
        toast(f"Selected: {project['name']}")

    # Navigation methods
    def navigate_to_data_exploration(self):
        """Navigate to data exploration screen"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        app = App.get_running_app()
        app.root.current = 'data_exploration'
        toast("Opening Data Exploration...")

    def navigate_to_qualitative_analytics(self):
        """Navigate to qualitative analytics screen"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        app = App.get_running_app()
        app.root.current = 'qualitative_analytics'
        toast("Opening Qualitative Analytics...")

    def navigate_to_descriptive_analytics(self):
        """Navigate to descriptive analytics screen"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        app = App.get_running_app()
        app.root.current = 'descriptive_analytics'
        toast("Opening Descriptive Analytics...")

    def navigate_to_auto_detection(self):
        """Navigate to auto detection screen"""
        if not self.current_project_id:
            toast("Please select a project first")
            return
        app = App.get_running_app()
        app.root.current = 'auto_detection'
        toast("Opening Auto Detection...")

    def toggle_project_overview(self):
        """Toggle the project overview collapsible state"""
        self.is_project_overview_collapsed = not self.is_project_overview_collapsed
        self.update_project_overview_collapse_state()
    
    def update_project_overview_collapse_state(self):
        """Update the visual state of the collapsible project overview"""
        try:
            if not hasattr(self.ids, 'project_overview_content') or not hasattr(self.ids, 'stats_toggle_button'):
                return
            
            content = self.ids.project_overview_content
            toggle_button = self.ids.stats_toggle_button
            project_overview_card = self.ids.project_overview_card
            
            if self.is_project_overview_collapsed:
                content.height = 0
                content.opacity = 0
                toggle_button.icon = "chevron-right"
                project_overview_card.height = dp(88)
            else:
                content.height = dp(176)
                content.opacity = 1
                toggle_button.icon = "chevron-down"
                project_overview_card.height = dp(264)
                
        except Exception as e:
            print(f"Error updating project overview collapse state: {e}")

    def update_quick_stats(self):
        """Update quick statistics using existing StatCard widget"""
        if not hasattr(self.ids, 'stats_container'):
            return
            
        try:
            stats_container = self.ids.stats_container
            stats_container.clear_widgets()
            
            if not self.current_project_id:
                return
                
            stats = self.get_project_stats()
            
            # Import the existing StatCard widget
            from widgets.stat_card import StatCard
            
            stat_items = [
                ("Total Responses", f"{stats.get('total_responses', 0):,}", "database-outline", 
                 "Survey responses collected"),
                ("Questions", f"{stats.get('total_questions', 0)}", "help-circle-outline", 
                 "Questions in survey"),
                ("Completion Rate", f"{stats.get('completion_rate', 0):.1f}%", "chart-line", 
                 "Response completion rate"),
                ("Participants", f"{stats.get('unique_respondents', 0):,}", "account-group-outline", 
                 "Unique respondents"),
            ]
            
            for title, value, icon, note in stat_items:
                try:
                    stat_card = StatCard(
                        title=title,
                        value=value,
                        icon=icon,
                        note=note
                    )
                    stats_container.add_widget(stat_card)
                except Exception as card_error:
                    print(f"Error creating stat card for {title}: {card_error}")
                    
        except Exception as e:
            print(f"Error updating quick stats: {e}")

    def get_project_stats(self):
        """Get enhanced project statistics"""
        if not self.current_project_id:
            return {}
            
        try:
            stats = self.analytics_service.get_project_stats(self.current_project_id)
            
            if 'error' in stats:
                print(f"Error getting project stats: {stats['error']}")
                return {}
            
            completion_rate = 0
            total_responses = stats.get('total_responses', 0)
            total_questions = stats.get('total_questions', 0)
            unique_respondents = stats.get('unique_respondents', 0)
            
            if total_questions > 0 and unique_respondents > 0:
                expected_total = total_questions * unique_respondents
                completion_rate = min(100, (total_responses / expected_total) * 100) if expected_total > 0 else 0
                
            return {
                'total_responses': total_responses,
                'total_questions': total_questions,
                'completion_rate': round(completion_rate, 1),
                'unique_respondents': unique_respondents,
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'data_quality_score': min(100, completion_rate + 10) if completion_rate > 0 else 0
            }
            
        except Exception as e:
            print(f"Error getting project stats: {e}")
            return {}

    def show_inferential_info(self):
        """Show information about inferential statistics"""
        toast("Inferential Statistics: Advanced statistical testing coming soon!")


    # Callback methods
    def show_project_selection_guide(self):
        """Show project selection guide"""
        toast("Select a project above to access analytics features")

    def navigate_to_projects(self):
        """Navigate to projects screen"""
        app = App.get_running_app()
        app.root.current = 'projects'
        toast("Opening Projects...")

    def on_window_resize(self, window, width, height):
        """Handle window resize"""
        self.update_responsive_layout()
        self.is_tablet = self._detect_tablet()

    def update_responsive_layout(self):
        """Update responsive layout"""
        try:
            window_width = Window.width
            window_height = Window.height
            
            if window_width < 800:
                stats_cols = 2
                card_spacing = dp(16)
            elif window_width < 1200:
                stats_cols = 4
                card_spacing = self.SPACING
            else:
                stats_cols = 4
                card_spacing = self.SPACING
                
            if hasattr(self.ids, 'stats_container'):
                container = self.ids.stats_container
                container.cols = stats_cols
                container.spacing = card_spacing
                
            if hasattr(self.ids, 'main_content'):
                if window_width > window_height:
                    self.ids.main_content.padding = [self.PADDING * 1.5, self.PADDING, self.PADDING * 1.5, self.PADDING]
                else:
                    self.ids.main_content.padding = [self.PADDING, self.PADDING * 1.5, self.PADDING, self.PADDING]
                
        except Exception as e:
            print(f"Error in responsive layout: {e}")
            if hasattr(self.ids, 'stats_container'):
                self.ids.stats_container.cols = 2