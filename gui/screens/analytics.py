from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.tab import MDTabsBase, MDTabs
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField
from kivymd.uix.slider import MDSlider

import threading
import json
from datetime import datetime

Builder.load_file('kv/analytics.kv')

class AnalyticsTab(MDBoxLayout, MDTabsBase):
    """Base class for analytics tab content"""
    pass

class AutoDetectionTab(AnalyticsTab):
    """Auto-detection and overview tab"""
    pass

class DescriptiveTab(AnalyticsTab):
    """Descriptive analytics tab"""
    pass

class InferentialTab(AnalyticsTab):
    """Inferential statistics tab"""
    pass

class QualitativeTab(AnalyticsTab):
    """Qualitative analytics tab"""
    pass

class AnalyticsScreen(Screen):
    # Properties
    current_project_id = StringProperty(None, allownone=True)
    current_project_name = StringProperty("")
    project_list = ListProperty([])
    project_map = {}
    
    # Analysis state
    is_loading = BooleanProperty(False)
    current_tab = StringProperty("auto_detection")
    analysis_results = ObjectProperty({})
    
    # UI references
    project_menu = None
    analytics_service = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.analysis_results = {}

    def on_enter(self):
        """Initialize analytics screen when entered"""
        Clock.schedule_once(self._delayed_init, 0.1)

    def _delayed_init(self, dt):
        """Delayed initialization to ensure all widgets are ready"""
        self.setup_analytics_service()
        self.load_projects()
        self.setup_tabs()
        self.update_quick_stats()

    def setup_analytics_service(self):
        """Initialize analytics service"""
        app = App.get_running_app()
        if not self.analytics_service:
            from services.analytics_service import AnalyticsService
            self.analytics_service = AnalyticsService(
                app.auth_service,
                app.db_service
            )

    def load_projects(self):
        """Load available projects for analysis"""
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
            
            if not projects:
                self.show_no_projects_state()
                return
                
            self.project_list = [
                {
                    'id': p['id'],
                    'name': p['name'],
                    'description': p['description'] or '',
                    'response_count': p['response_count'] or 0,
                    'created_at': p['created_at']
                }
                for p in projects
            ]
            
            self.project_map = {p['name']: p['id'] for p in projects}
            
            # Update project selector
            if hasattr(self.ids, 'project_selector'):
                self.ids.project_selector.text = "Select Project for Analysis"
                
        except Exception as e:
            print(f"Error loading projects: {e}")
            toast("Error loading projects")
        finally:
            if conn:
                conn.close()

    def show_no_projects_state(self):
        """Show message when no projects are available"""
        toast("No projects found. Create a project first to analyze data.")

    def open_project_menu(self):
        """Open project selection dropdown menu"""
        if self.project_menu:
            self.project_menu.dismiss()
            
        if not self.project_list:
            toast("No projects available")
            return
            
        menu_items = []
        for project in self.project_list:
            menu_items.append({
                "text": f"{project['name']} ({project['response_count']} responses)",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=project: self.select_project(x)
            })
            
        self.project_menu = MDDropdownMenu(
            caller=self.ids.project_selector,
            items=menu_items,
            width_mult=4
        )
        self.project_menu.open()

    def select_project(self, project):
        """Select a project for analysis"""
        if self.project_menu:
            self.project_menu.dismiss()
            
        self.current_project_id = project['id']
        self.current_project_name = project['name']
        self.ids.project_selector.text = project['name']
        
        # Update quick stats for selected project
        self.update_quick_stats()
        
        # Load data characteristics for auto-detection
        self.load_project_data_characteristics()
        
        toast(f"Selected project: {project['name']}")

    def setup_tabs(self):
        """Setup the analytics tabs"""
        if not hasattr(self.ids, 'analytics_tabs'):
            return
            
        tabs = self.ids.analytics_tabs
        tabs.bind(on_tab_switch=self.on_tab_switch)

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        """Handle tab switching"""
        tab_map = {
            "Auto-Detection": "auto_detection",
            "Descriptive": "descriptive", 
            "Inferential": "inferential",
            "Qualitative": "qualitative"
        }
        
        self.current_tab = tab_map.get(tab_text, "auto_detection")
        self.load_tab_content()

    def load_tab_content(self):
        """Load content for the current tab"""
        if not self.current_project_id:
            return
            
        if self.current_tab == "auto_detection":
            self.load_auto_detection()
        elif self.current_tab == "descriptive":
            self.load_descriptive()
        elif self.current_tab == "inferential":
            self.load_inferential()
        elif self.current_tab == "qualitative":
            self.load_qualitative()

    def update_quick_stats(self):
        """Update the quick statistics cards"""
        if not hasattr(self.ids, 'stats_container'):
            return
            
        try:
            stats = self.get_project_stats()
            self.ids.stats_container.clear_widgets()
            
            # Create stat cards
            stat_items = [
                ("Total Responses", stats.get('total_responses', 0), "chart-line"),
                ("Questions", stats.get('total_questions', 0), "help-circle"),
                ("Completion Rate", f"{stats.get('completion_rate', 0)}%", "check-circle"),
                ("Last Updated", stats.get('last_updated', 'Never'), "clock")
            ]
            
            for label, value, icon in stat_items:
                card = self.create_stat_card(label, str(value), icon)
                self.ids.stats_container.add_widget(card)
                
        except Exception as e:
            print(f"Error updating quick stats: {e}")

    def get_project_stats(self):
        """Get statistics for the current project"""
        if not self.current_project_id:
            return {}
            
        try:
            app = App.get_running_app()
            conn = app.db_service.get_db_connection()
            cursor = conn.cursor()
            
            # Get response count
            cursor.execute("""
                SELECT COUNT(*) as total_responses
                FROM responses 
                WHERE project_id = ?
            """, (self.current_project_id,))
            response_data = cursor.fetchone()
            
            # Get question count
            cursor.execute("""
                SELECT COUNT(*) as total_questions
                FROM questions 
                WHERE project_id = ? 
            """, (self.current_project_id,))
            question_data = cursor.fetchone()
            
            # Calculate completion rate (simplified)
            cursor.execute("""
                SELECT COUNT(DISTINCT respondent_id) as unique_respondents
                FROM responses 
                WHERE project_id = ?
            """, (self.current_project_id,))
            respondent_data = cursor.fetchone()
            
            total_responses = response_data['total_responses'] if response_data else 0
            total_questions = question_data['total_questions'] if question_data else 0
            unique_respondents = respondent_data['unique_respondents'] if respondent_data else 0
            
            # Simple completion rate calculation
            completion_rate = 0
            if total_questions > 0 and unique_respondents > 0:
                expected_total = total_questions * unique_respondents
                completion_rate = min(100, (total_responses / expected_total) * 100) if expected_total > 0 else 0
                
            return {
                'total_responses': total_responses,
                'total_questions': total_questions,
                'completion_rate': round(completion_rate, 1),
                'unique_respondents': unique_respondents,
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
        except Exception as e:
            print(f"Error getting project stats: {e}")
            return {}
        finally:
            if 'conn' in locals():
                conn.close()

    def create_stat_card(self, title, value, icon):
        """Create a statistics card widget"""
        from widgets.stat_card import StatCard
        return StatCard(title=title, value=value, icon=icon)

    def load_project_data_characteristics(self):
        """Load data characteristics for auto-detection"""
        if not self.current_project_id:
            return
            
        # This will be used by auto-detection
        threading.Thread(
            target=self._load_data_characteristics_thread,
            daemon=True
        ).start()

    def _load_data_characteristics_thread(self):
        """Background thread to load data characteristics"""
        try:
            if self.analytics_service:
                characteristics = self.analytics_service.get_data_characteristics(
                    self.current_project_id
                )
                Clock.schedule_once(
                    lambda dt: self._update_data_characteristics(characteristics), 0
                )
        except Exception as e:
            print(f"Error loading data characteristics: {e}")

    def _update_data_characteristics(self, characteristics):
        """Update UI with data characteristics"""
        self.analysis_results['data_characteristics'] = characteristics

    # Analysis Methods
    
    def load_auto_detection(self):
        """Load auto-detection recommendations"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
            
        self.set_loading(True)
        threading.Thread(target=self._load_auto_detection_thread, daemon=True).start()

    def _load_auto_detection_thread(self):
        """Background thread for auto-detection"""
        try:
            if self.analytics_service:
                recommendations = self.analytics_service.get_analysis_recommendations(
                    self.current_project_id
                )
                Clock.schedule_once(
                    lambda dt: self._display_auto_detection(recommendations), 0
                )
        except Exception as e:
            print(f"Error in auto-detection: {e}")
            Clock.schedule_once(lambda dt: self.show_error("Auto-detection failed"), 0)
        finally:
            Clock.schedule_once(lambda dt: self.set_loading(False), 0)

    def _display_auto_detection(self, recommendations):
        """Display auto-detection recommendations"""
        if not hasattr(self.ids, 'auto_detection_content'):
            return
            
        content = self.ids.auto_detection_content
        content.clear_widgets()
        
        if not recommendations:
            content.add_widget(MDLabel(
                text="No analysis recommendations available",
                halign="center",
                theme_text_color="Secondary"
            ))
            return
            
        # Display recommendations
        for category, recs in recommendations.items():
            if recs and isinstance(recs, list):
                # Category header
                header = MDLabel(
                    text=category.replace('_', ' ').title(),
                    font_style="H6",
                    theme_text_color="Primary",
                    size_hint_y=None,
                    height=dp(40)
                )
                content.add_widget(header)
                
                # Recommendations
                for rec in recs[:3]:  # Show top 3 recommendations
                    rec_card = self.create_recommendation_card(rec)
                    content.add_widget(rec_card)

    def create_recommendation_card(self, recommendation):
        """Create a recommendation card"""
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(120),
            elevation=2
        )
        
        # Recommendation title
        title = MDLabel(
            text=recommendation.get('method', 'Unknown Method'),
            font_style="Subtitle1",
            theme_text_color="Primary"
        )
        card.add_widget(title)
        
        # Recommendation description
        desc = MDLabel(
            text=recommendation.get('rationale', 'No description available'),
            font_style="Body2",
            theme_text_color="Secondary"
        )
        card.add_widget(desc)
        
        # Action button
        action_btn = MDRaisedButton(
            text="Run Analysis",
            size_hint=(None, None),
            height=dp(36),
            width=dp(120)
        )
        card.add_widget(action_btn)
        
        return card

    def load_descriptive(self):
        """Load descriptive analytics"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
            
        self.set_loading(True)
        threading.Thread(target=self._load_descriptive_thread, daemon=True).start()

    def _load_descriptive_thread(self):
        """Background thread for descriptive analytics"""
        try:
            if self.analytics_service:
                results = self.analytics_service.run_descriptive_analysis(
                    self.current_project_id
                )
                Clock.schedule_once(
                    lambda dt: self._display_descriptive_results(results), 0
                )
        except Exception as e:
            print(f"Error in descriptive analysis: {e}")
            Clock.schedule_once(lambda dt: self.show_error("Descriptive analysis failed"), 0)
        finally:
            Clock.schedule_once(lambda dt: self.set_loading(False), 0)

    def _display_descriptive_results(self, results):
        """Display descriptive analysis results"""
        if not hasattr(self.ids, 'descriptive_content'):
            return
            
        content = self.ids.descriptive_content
        content.clear_widgets()
        
        if not results:
            content.add_widget(MDLabel(
                text="No descriptive analysis results available",
                halign="center",
                theme_text_color="Secondary"
            ))
            return
            
        # Display basic statistics
        stats_card = self.create_stats_display_card(results)
        content.add_widget(stats_card)

    def create_stats_display_card(self, results):
        """Create statistics display card"""
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(200),
            elevation=2
        )
        
        title = MDLabel(
            text="Basic Statistics",
            font_style="H6",
            theme_text_color="Primary"
        )
        card.add_widget(title)
        
        # Add statistics content
        stats_text = str(results)  # Simplified for now
        stats_label = MDLabel(
            text=stats_text,
            font_style="Body2",
            theme_text_color="Secondary"
        )
        card.add_widget(stats_label)
        
        return card

    def load_inferential(self):
        """Load inferential statistics"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
            
        toast("Inferential statistics coming soon!")

    def load_qualitative(self):
        """Load qualitative analytics"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
            
        toast("Qualitative analytics coming soon!")

    # Utility Methods
    
    def show_select_project_message(self):
        """Show message to select a project first"""
        toast("Please select a project first")

    def set_loading(self, loading):
        """Set loading state"""
        self.is_loading = loading
        if hasattr(self.ids, 'loading_spinner'):
            self.ids.loading_spinner.active = loading

    def show_error(self, message):
        """Show error message"""
        toast(f"Error: {message}")

    def refresh_analysis(self):
        """Refresh current analysis"""
        if self.current_project_id:
            self.load_tab_content()
        else:
            toast("Select a project first")

    def export_results(self):
        """Export analysis results"""
        if not self.analysis_results:
            toast("No results to export")
            return
            
        toast("Export functionality coming soon!")

    def show_analysis_config(self):
        """Show analysis configuration dialog"""
        toast("Analysis configuration coming soon!") 