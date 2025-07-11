from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
from utils.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton
from kivymd.uix.card import MDCard
# Updated imports for KivyMD 2.0.0 - simplified approach
from kivymd.uix.menu import MDDropdownMenu
from kivy.core.window import Window
from widgets.top_bar import TopBar

import threading
import json
from datetime import datetime

Builder.load_file('kv/analytics.kv')

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
        Window.bind(on_resize=self.on_window_resize)

    def on_enter(self):
        """Initialize analytics screen when entered"""
        Clock.schedule_once(self._delayed_init, 0.1)

    def _delayed_init(self, dt):
        """Delayed initialization to ensure all widgets are ready"""
        # Set top bar title for consistency
        if hasattr(self.ids, 'top_bar'):
            self.ids.top_bar.set_title("Analytics")
        
        self.setup_analytics_service()
        self.load_projects()
        self.setup_tabs()
        
        # Clean up any overlapping widgets
        self.cleanup_overlapping_widgets()
        
        # Initialize responsive layout
        self.update_responsive_layout()
        
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

    def cleanup_overlapping_widgets(self):
        """Clean up any potentially overlapping widgets that could cause text mangling"""
        try:
            # Clear stats container to prevent overlapping
            if hasattr(self.ids, 'stats_container'):
                stats_container = getattr(self.ids, 'stats_container', None)
                if stats_container:
                    stats_container.clear_widgets()
            
            # Ensure project selector has clean text
            if hasattr(self.ids, 'project_selector'):
                project_selector = getattr(self.ids, 'project_selector', None)
                if project_selector:
                    project_selector.text = "Select Project for Analysis"
                    
        except Exception as e:
            print(f"Error cleaning up overlapping widgets: {e}")

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
        
        # Clear and set project selector text properly
        if hasattr(self.ids, 'project_selector'):
            self.ids.project_selector.text = project['name']
        
        # Update quick stats for selected project
        self.update_quick_stats()
        
        # Load data characteristics for auto-detection
        self.load_project_data_characteristics()
        
        toast(f"Selected project: {project['name']}")

    def setup_tabs(self):
        """Setup the analytics tabs with simple button-based approach"""
        # Set initial tab state
        self.current_tab = "auto_detection"
        self.update_tab_buttons()
        
    def switch_to_tab(self, tab_name):
        """Switch to a specific tab"""
        self.current_tab = tab_name
        self.update_tab_buttons()
        self.load_tab_content()
        
    def update_tab_buttons(self):
        """Update the visual state of tab buttons"""
        try:
            # Get app theme colors
            app = App.get_running_app()
            primary_color = app.theme_cls.primary_color
            surface_color = getattr(app.theme_cls, 'surface_color', (0.98, 0.98, 0.98, 1))
            
            # Button IDs and corresponding tab names
            buttons = {
                'auto_detection_tab_btn': 'auto_detection',
                'descriptive_tab_btn': 'descriptive',
                'inferential_tab_btn': 'inferential',
                'qualitative_tab_btn': 'qualitative'
            }
            
            # Update button styles based on current tab
            for btn_id, tab_name in buttons.items():
                if hasattr(self.ids, btn_id):
                    button = getattr(self.ids, btn_id)
                    if tab_name == self.current_tab:
                        # Active tab styling
                        button.md_bg_color = primary_color
                        button.theme_text_color = "Custom"
                        button.text_color = (1, 1, 1, 1)  # White text
                    else:
                        # Inactive tab styling
                        button.md_bg_color = surface_color
                        button.theme_text_color = "Primary"
                        
        except Exception as e:
            print(f"Error updating tab buttons: {e}")

    def load_tab_content(self):
        """Load content for the current tab"""
        if not hasattr(self.ids, 'tab_content_area'):
            return
            
        content_area = self.ids.tab_content_area
        content_area.clear_widgets()
        
        if not self.current_project_id:
            # Show project selection message
            content_area.add_widget(MDLabel(
                text="Please select a project above to view analysis options",
                halign="center",
                theme_text_color="Secondary",
                font_style="Body",
                font_size="16sp"
            ))
            return
            
        # Load content based on current tab
        if self.current_tab == "auto_detection":
            self.load_auto_detection_content()
        elif self.current_tab == "descriptive":
            self.load_descriptive_content()
        elif self.current_tab == "inferential":
            self.load_inferential_content()
        elif self.current_tab == "qualitative":
            self.load_qualitative_content()
            
    def load_auto_detection_content(self):
        """Load auto-detection tab content"""
        content_area = self.ids.tab_content_area
        
        # Add title
        title_label = MDLabel(
            text="Auto-Detection Analysis",
            font_style="Title",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(48)
        )
        content_area.add_widget(title_label)
        
        # Add description
        desc_label = MDLabel(
            text="Automatically detect appropriate analysis methods based on your data",
            halign="center",
            theme_text_color="Secondary",
            font_style="Body",
            font_size="14sp"
        )
        content_area.add_widget(desc_label)
        
        # Add run button
        run_button = MDButton(
            text="Run Auto-Detection",
            style="elevated",
            size_hint=(None, None),
            size=(dp(200), dp(48)),
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.load_auto_detection()
        )
        content_area.add_widget(run_button)
        
    def load_descriptive_content(self):
        """Load descriptive analysis tab content"""
        content_area = self.ids.tab_content_area
        
        # Add title
        title_label = MDLabel(
            text="Descriptive Analysis",
            font_style="Title",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(48)
        )
        content_area.add_widget(title_label)
        
        # Add description
        desc_label = MDLabel(
            text="Generate descriptive statistics and summaries for your data",
            halign="center",
            theme_text_color="Secondary",
            font_style="Body",
            font_size="14sp"
        )
        content_area.add_widget(desc_label)
        
        # Add run button
        run_button = MDButton(
            text="Run Descriptive Analysis",
            style="elevated",
            size_hint=(None, None),
            size=(dp(200), dp(48)),
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.load_descriptive()
        )
        content_area.add_widget(run_button)
        
    def load_inferential_content(self):
        """Load inferential analysis tab content"""
        content_area = self.ids.tab_content_area
        
        # Add title
        title_label = MDLabel(
            text="Inferential Analysis",
            font_style="Title",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(48)
        )
        content_area.add_widget(title_label)
        
        # Add description
        desc_label = MDLabel(
            text="Perform statistical tests and inference on your data",
            halign="center",
            theme_text_color="Secondary",
            font_style="Body",
            font_size="14sp"
        )
        content_area.add_widget(desc_label)
        
        # Add run button
        run_button = MDButton(
            text="Run Inferential Analysis",
            style="elevated",
            size_hint=(None, None),
            size=(dp(200), dp(48)),
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.load_inferential()
        )
        content_area.add_widget(run_button)
        
    def load_qualitative_content(self):
        """Load qualitative analysis tab content"""
        content_area = self.ids.tab_content_area
        
        # Add title
        title_label = MDLabel(
            text="Qualitative Analysis",
            font_style="Title",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(48)
        )
        content_area.add_widget(title_label)
        
        # Add description
        desc_label = MDLabel(
            text="Analyze text and qualitative data using NLP techniques",
            halign="center",
            theme_text_color="Secondary",
            font_style="Body",
            font_size="14sp"
        )
        content_area.add_widget(desc_label)
        
        # Add run button
        run_button = MDButton(
            text="Run Qualitative Analysis",
            style="elevated",
            size_hint=(None, None),
            size=(dp(200), dp(48)),
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.load_qualitative()
        )
        content_area.add_widget(run_button)

    def update_quick_stats(self):
        """Update the quick statistics cards with tablet optimization"""
        if not hasattr(self.ids, 'stats_container'):
            return
        try:
            stats_container = getattr(self.ids, 'stats_container', None)
            if not stats_container:
                return
            stats_container.clear_widgets()
            stats = self.get_project_stats()
            if not self.current_project_id:
                return
            # Use a grid layout for 2 cards per row
            stats_container.cols = 2
            stat_items = [
                ("Total Responses", stats.get('total_responses', 0), "database", "From your accessible projects"),
                ("Questions", stats.get('total_questions', 0), "help-circle", "Questions in this project"),
                ("Completion Rate", f"{stats.get('completion_rate', 0)}%", "check-circle", "Survey completion rate"),
                ("Last Updated", stats.get('last_updated', 'Never'), "clock", "Most recent update"),
            ]
            from widgets.analytics_stat_card import AnalyticsStatCard
            for label, value, icon, note in stat_items:
                try:
                    card = AnalyticsStatCard(title=label, value=str(value), icon=icon, note=note)
                    if card:
                        stats_container.add_widget(card)
                except Exception as card_error:
                    print(f"Error creating analytics stat card for {label}: {card_error}")
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

    def create_tablet_optimized_stat_card(self, title, value, icon):
        """Create a tablet-optimized statistics card"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            from widgets.stat_card import StatCard
            
            category = ResponsiveHelper.get_screen_size_category()
            
            # Adjust card size based on device category
            if category in ["tablet", "large_tablet"]:
                card = StatCard(
                    title=title, 
                    value=str(value), 
                    icon=icon,
                    size_hint=(None, None),
                    size=(dp(180), dp(80)),  # Larger for tablets
                )
            else:
                card = StatCard(
                    title=title, 
                    value=str(value), 
                    icon=icon,
                    size_hint=(None, None),
                    size=(dp(140), dp(60)),  # Standard size
                )
                
            return card
            
        except Exception as e:
            print(f"Error creating tablet stat card: {e}")
            # Fallback to original method
            return self.create_stat_card(title, value, icon)

    def create_stat_card(self, title, value, icon):
        """Create a statistics card widget"""
        from widgets.stat_card import StatCard
        return StatCard(title=title, value=value, icon=icon)

    def create_clean_stat_card(self, title, value, icon):
        """Create a clean statistics card without overlapping text"""
        try:
            from widgets.stat_card import StatCard
            
            # Create stat card with clean properties
            card = StatCard(
                title=str(title).strip(),
                value=str(value).strip(), 
                icon=icon,
                size_hint=(None, None),
                size=(dp(160), dp(70))
            )
            return card
            
        except Exception as e:
            print(f"Error creating clean stat card: {e}")
            # Fallback to basic card creation
            try:
                from kivymd.uix.card import MDCard
                from kivymd.uix.label import MDLabel
                from kivymd.uix.boxlayout import MDBoxLayout
                
                card = MDCard(
                    size_hint=(None, None),
                    size=(dp(160), dp(70)),
                    elevation=1,
                    padding=dp(8)
                )
                
                layout = MDBoxLayout(
                    orientation='vertical',
                    spacing=dp(4)
                )
                
                title_label = MDLabel(
                    text=str(title).strip(),
                    font_style="Caption",
                    theme_text_color="Secondary",
                    halign="center",
                    size_hint_y=None,
                    height=dp(20)
                )
                
                value_label = MDLabel(
                    text=str(value).strip(),
                    font_style="H6",
                    theme_text_color="Primary", 
                    halign="center",
                    size_hint_y=None,
                    height=dp(30)
                )
                
                layout.add_widget(title_label)
                layout.add_widget(value_label)
                card.add_widget(layout)
                
                return card
                
            except Exception as fallback_error:
                print(f"Error creating fallback stat card: {fallback_error}")
                return None

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
        """Display auto-detection recommendations with tablet optimization"""
        if not hasattr(self.ids, 'auto_detection_content'):
            return
            
        content = self.ids.auto_detection_content
        content.clear_widgets()
        
        if not recommendations:
            content.add_widget(MDLabel(
                text="No analysis recommendations available",
                halign="center",
                theme_text_color="Secondary",
                font_size="16sp"
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
                    height=dp(48),
                    font_size="20sp"
                )
                content.add_widget(header)
                
                # Recommendations
                for rec in recs[:3]:  # Show top 3 recommendations
                    rec_card = self.create_tablet_optimized_recommendation_card(rec)
                    content.add_widget(rec_card)

    def create_tablet_optimized_recommendation_card(self, recommendation):
        """Create a tablet-optimized recommendation card"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            
            category = ResponsiveHelper.get_screen_size_category()
            
            # Responsive card sizing
            if category in ["tablet", "large_tablet"]:
                card_height = dp(150)
                button_height = dp(48)
                font_sizes = {"title": "18sp", "desc": "16sp", "button": "16sp"}
            else:
                card_height = dp(120)
                button_height = dp(36)
                font_sizes = {"title": "16sp", "desc": "14sp", "button": "14sp"}
            
            card = MDCard(
                orientation="vertical",
                padding=dp(20),
                spacing=dp(12),
                size_hint_y=None,
                height=card_height,
                elevation=2
            )
            
            # Recommendation title
            title = MDLabel(
                text=recommendation.get('method', 'Unknown Method'),
                font_style="Subtitle1",
                theme_text_color="Primary",
                font_size=font_sizes["title"]
            )
            card.add_widget(title)
            
            # Recommendation description
            desc = MDLabel(
                text=recommendation.get('rationale', 'No description available'),
                font_style="Body2",
                theme_text_color="Secondary",
                font_size=font_sizes["desc"],
                text_size=(None, None)
            )
            card.add_widget(desc)
            
            # Action button
            action_btn = MDButton(
                style="elevated",
                text="Run Analysis",
                size_hint=(None, None),
                height=button_height,
                width=dp(140),
                font_size=font_sizes["button"]
            )
            card.add_widget(action_btn)
            
            return card
            
        except Exception as e:
            print(f"Error creating tablet recommendation card: {e}")
            # Fallback to original method
            return self.create_recommendation_card(recommendation)

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
        action_btn = MDButton(
            style="elevated",
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
        toast("Analysis configuration coming soon")
        
    def on_window_resize(self, window, width, height):
        self.update_responsive_layout()

    def update_responsive_layout(self):
        # Responsive columns for stat cards
        try:
            window_width = Window.width
            min_card_width = 320  # match dashboard style
            spacing = 24
            padding = 48  # left+right
            available_width = window_width - padding
            max_possible_cols = max(1, int(available_width / (min_card_width + spacing)))
            if window_width < 700:
                stats_cols = 1
            elif window_width < 1200:
                stats_cols = 2
            elif window_width < 1600:
                stats_cols = min(3, max_possible_cols)
            else:
                stats_cols = min(4, max_possible_cols)
            stats_cols = min(stats_cols, 4)
            stats_cols = max(stats_cols, 1)
            if hasattr(self.ids, 'stats_container'):
                self.ids.stats_container.cols = stats_cols
                self.ids.stats_container.do_layout()
        except Exception as e:
            print(f"Error in analytics responsive layout: {e}")
            if hasattr(self.ids, 'stats_container'):
                self.ids.stats_container.cols = 1
                self.ids.stats_container.do_layout()