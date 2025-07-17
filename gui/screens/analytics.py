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
            if hasattr(self.ids, 'project_selector_text'):
                project_selector_text = getattr(self.ids, 'project_selector_text', None)
                if project_selector_text:
                    project_selector_text.text = "Select Project for Analysis"
            elif hasattr(self.ids, 'project_selector'):
                project_selector = getattr(self.ids, 'project_selector', None)
                if project_selector and hasattr(project_selector, 'text'):
                    project_selector.text = "Select Project for Analysis"
                    
        except Exception as e:
            print(f"Error cleaning up overlapping widgets: {e}")

    def load_projects(self):
        """Load available projects that have collected responses for analysis"""
        try:
            app = App.get_running_app()
            
            # Ensure we have proper authentication
            if not app.auth_service.is_authenticated():
                toast("Please log in to access analytics")
                return
            
            conn = app.db_service.get_db_connection()
            
            if conn is None:
                toast("Database not initialized")
                return
                
            cursor = conn.cursor()
            user_data = app.auth_service.get_user_data()
            user_id = user_data.get('id') if user_data else None
            
            print(f"Analytics: Loading projects with responses for user_id: {user_id}")
            
            if user_id:
                # Load projects that have responses for the authenticated user
                # Updated query to work with GUI SQLite database structure
                cursor.execute("""
                    SELECT DISTINCT p.id, p.name, p.description, p.created_at,
                           COUNT(r.response_id) as response_count,
                           COUNT(DISTINCT r.respondent_id) as respondent_count,
                           COUNT(DISTINCT q.id) as question_count
                    FROM projects p
                    INNER JOIN responses r ON p.id = r.project_id AND r.user_id = ?
                    LEFT JOIN questions q ON p.id = q.project_id AND q.user_id = ?
                    WHERE p.user_id = ?
                    GROUP BY p.id, p.name, p.description, p.created_at
                    HAVING COUNT(r.response_id) > 0
                    ORDER BY p.name
                """, (user_id, user_id, user_id))
            else:
                # Fallback: load all projects with responses (for backward compatibility)
                cursor.execute("""
                    SELECT DISTINCT p.id, p.name, p.description, p.created_at,
                           COUNT(r.response_id) as response_count,
                           COUNT(DISTINCT r.respondent_id) as respondent_count,
                           COUNT(DISTINCT q.id) as question_count
                    FROM projects p
                    INNER JOIN responses r ON p.id = r.project_id
                    LEFT JOIN questions q ON p.id = q.project_id
                    GROUP BY p.id, p.name, p.description, p.created_at
                    HAVING COUNT(r.response_id) > 0
                    ORDER BY p.name
                """)
                
            projects = cursor.fetchall()
            
            print(f"Analytics: Found {len(projects)} projects with responses")
            
            if not projects:
                self.show_no_projects_state()
                return
                
            self.project_list = [
                {
                    'id': p['id'],
                    'name': p['name'],
                    'description': p['description'] or '',
                    'response_count': p['response_count'] or 0,
                    'respondent_count': p['respondent_count'] or 0,
                    'question_count': p['question_count'] or 0,
                    'created_at': p['created_at']
                }
                for p in projects
            ]
            
            self.project_map = {p['name']: p['id'] for p in projects}
            
            # Update project selector
            if hasattr(self.ids, 'project_selector_text'):
                self.ids.project_selector_text.text = "Select Project for Analysis"
            elif hasattr(self.ids, 'project_selector'):
                if hasattr(self.ids.project_selector, 'text'):
                    self.ids.project_selector.text = "Select Project for Analysis"
                
            print(f"Analytics: Successfully loaded {len(self.project_list)} projects with data")
            
            # Debug: Print project statistics
            for project in self.project_list:
                print(f"  Project '{project['name']}': {project['response_count']} responses, {project['respondent_count']} respondents, {project['question_count']} questions")
                
        except Exception as e:
            print(f"Error loading projects: {e}")
            import traceback
            traceback.print_exc()
            toast(f"Error loading projects: {str(e)}")
        finally:
            if conn:
                conn.close()

    def show_no_projects_state(self):
        """Show message when no projects with responses are found"""
        try:
            # Clear any existing content first
            if hasattr(self.ids, 'main_content'):
                self.ids.main_content.clear_widgets()
            
            # Create a comprehensive no-data state with better instructions
            no_data_card = MDCard(
                orientation="vertical",
                padding=dp(32),
                spacing=dp(16),
                size_hint_y=None,
                height=dp(300),  # Increased height for more content
                elevation=2
            )
            
            title_label = MDLabel(
                text="No Analytics Data Available",
                theme_text_color="Primary",
                halign="center",
                size_hint_y=None,
                height=dp(40)
            )
            
            # More detailed instructions
            message_label = MDLabel(
                text="To see analytics, you need projects with collected responses.\n\nYour current status:\n• Projects created: Available\n• Questions defined: Available\n• Data collected: None\n\nNext steps:\n1. Go to the Data Collection tab\n2. Select a project and start collecting responses\n3. Return here to analyze your data",
                halign="center",
                theme_text_color="Secondary",
                text_size=(dp(400), None),
                size_hint_y=None,
                height=dp(180)
            )
            
            # Add a helpful action button
            action_button = MDButton(
                text="Go to Data Collection",
                size_hint=(None, None),
                size=(dp(200), dp(40)),
                pos_hint={'center_x': 0.5},
                on_release=lambda x: self.go_to_data_collection()
            )
            
            no_data_card.add_widget(title_label)
            no_data_card.add_widget(message_label)
            no_data_card.add_widget(action_button)
            
            if hasattr(self.ids, 'main_content'):
                self.ids.main_content.add_widget(no_data_card)
                
        except Exception as e:
            print(f"Error creating no-data state: {e}")
            # Fallback to toast message
            toast("No projects with collected responses found. Start collecting data to see analytics.")
    
    def go_to_data_collection(self):
        """Navigate to the data collection screen"""
        try:
            app = App.get_running_app()
            if hasattr(app.root, 'switch_to_screen'):
                app.root.switch_to_screen('data_collection')
            elif hasattr(app.root, 'current'):
                app.root.current = 'data_collection'
        except Exception as e:
            print(f"Error navigating to data collection: {e}")
            toast("Please use the navigation menu to go to Data Collection")

    def open_project_menu(self):
        """Open project selection dropdown menu"""
        if self.project_menu:
            self.project_menu.dismiss()
            
        if not self.project_list:
            toast("No projects with responses found. Collect some data first.")
            return
            
        menu_items = []
        for project in self.project_list:
            # Show comprehensive information about each project
            response_count = project.get('response_count', 0)
            respondent_count = project.get('respondent_count', 0)
            question_count = project.get('question_count', 0)
            
            display_text = f"{project['name']}\n{response_count} responses • {respondent_count} respondents • {question_count} questions"
            
            menu_items.append({
                "text": display_text,
                "on_release": lambda x=project: self.select_project(x)
            })
            
        self.project_menu = MDDropdownMenu(
            caller=self.ids.project_selector,
            items=menu_items,
            width_mult=5,  # Increased width to accommodate more information
            max_height=dp(400)
        )
        self.project_menu.open()

    def select_project(self, project):
        """Select a project for analysis with comprehensive validation"""
        try:
            if self.project_menu:
                self.project_menu.dismiss()
                
            self.current_project_id = project['id']
            self.current_project_name = project['name']
            
            # Clear and set project selector text properly
            if hasattr(self.ids, 'project_selector_text'):
                # For KivyMD 2.0+ button, update the MDButtonText widget directly
                self.ids.project_selector_text.text = project['name']
            elif hasattr(self.ids, 'project_selector'):
                # Fallback for older versions
                button = self.ids.project_selector
                if hasattr(button, 'text'):
                    button.text = project['name']
            
            # Update quick stats for selected project
            self.update_quick_stats()
            
            # Perform comprehensive validation
            self.validate_project_and_update_ui()
            
            toast(f"Selected project: {project['name']}")
                
        except Exception as e:
            print(f"Error selecting project: {e}")
            import traceback
            traceback.print_exc()
            toast(f"Error selecting project: {str(e)}")

    def validate_project_and_update_ui(self):
        """Validate selected project and update UI with status information"""
        if not self.current_project_id or not self.analytics_service:
            return
            
        try:
            # Get comprehensive validation and status info
            status_info = self.analytics_service.get_analysis_status_info(self.current_project_id)
            validation = status_info.get('validation', {})
            backend_info = status_info.get('backend', {})
            
            # Update UI based on validation results
            self.update_validation_display(validation, backend_info)
            
            # Update tab availability
            self.update_tab_availability(validation.get('available_analyses', []))
            
            # Load tab content with validation context
            self.load_tab_content()
            
        except Exception as e:
            print(f"Error in project validation: {e}")
            self.show_validation_error(str(e))

    def update_validation_display(self, validation: dict, backend_info: dict):
        """Update UI to show validation status and warnings"""
        # Clear previous validation messages
        self.clear_validation_messages()
        
        # Show validation results in tab content if there are issues
        if validation.get('errors') or validation.get('warnings'):
            self.show_validation_summary(validation, backend_info)

    def clear_validation_messages(self):
        """Clear previous validation messages from UI"""
        # This will be called before showing new validation info
        pass

    def show_validation_summary(self, validation: dict, backend_info: dict):
        """Show comprehensive validation summary in the UI"""
        if not hasattr(self.ids, 'tab_content_area'):
            return
            
        content_area = self.ids.tab_content_area
        
        # Create validation status card
        validation_card = self.create_validation_status_card(validation, backend_info)
        if validation_card:
            # Insert at the beginning of content area
            content_area.add_widget(validation_card, index=len(content_area.children))

    def create_validation_status_card(self, validation: dict, backend_info: dict):
        """Create a comprehensive validation status card"""
        try:
            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel
            from kivymd.uix.boxlayout import MDBoxLayout
            from kivymd.uix.button import MDButton
            
            # Determine overall status
            has_errors = len(validation.get('errors', [])) > 0
            has_warnings = len(validation.get('warnings', [])) > 0
            
            if has_errors:
                status_color = (1, 0.2, 0.2, 1)  # Red
                status_text = "Issues Found"
                status_icon = "alert-circle"
            elif has_warnings:
                status_color = (1, 0.6, 0, 1)  # Orange
                status_text = "Warnings"
                status_icon = "alert"
            else:
                status_color = (0.2, 0.8, 0.2, 1)  # Green
                status_text = "Ready for Analysis"
                status_icon = "check-circle"
            
            card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(12),
                size_hint_y=None,
                height=dp(200) if has_errors or has_warnings else dp(120),
                elevation=2,
                md_bg_color=(0.98, 0.98, 0.98, 1)
            )
            
            # Status header
            header_layout = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(12),
                size_hint_y=None,
                height=dp(32)
            )
            
            status_label = MDLabel(
                text=f"📊 Project Status: {status_text}",
                theme_text_color="Primary",
                font_size="16sp",
                size_hint_x=1
            )
            header_layout.add_widget(status_label)
            
            # Backend status
            backend_status = "🟢 Online" if backend_info.get('available') else "🔴 Offline"
            backend_label = MDLabel(
                text=f"Backend: {backend_status}",
                theme_text_color="Secondary",
                font_size="12sp",
                size_hint_x=None,
                width=dp(100)
            )
            header_layout.add_widget(backend_label)
            
            card.add_widget(header_layout)
            
            # Data summary
            data_summary = validation.get('data_summary', {})
            if data_summary:
                summary_text = f"📈 {data_summary.get('total_responses', 0)} responses • {data_summary.get('unique_respondents', 0)} respondents • {data_summary.get('completion_rate', 0):.1f}% complete"
                summary_label = MDLabel(
                    text=summary_text,
                    theme_text_color="Secondary",
                    font_size="14sp",
                    size_hint_y=None,
                    height=dp(24)
                )
                card.add_widget(summary_label)
            
            # Available analyses
            available_analyses = validation.get('available_analyses', [])
            if available_analyses:
                analyses_text = f"✅ Available: {', '.join(available_analyses)}"
                analyses_label = MDLabel(
                    text=analyses_text,
                    theme_text_color="Primary",
                    font_size="14sp",
                    size_hint_y=None,
                    height=dp(24)
                )
                card.add_widget(analyses_label)
            
            # Errors
            errors = validation.get('errors', [])
            if errors:
                error_label = MDLabel(
                    text="❌ Issues:",
                    theme_text_color="Error",
                    font_size="14sp",
                    size_hint_y=None,
                    height=dp(20)
                )
                card.add_widget(error_label)
                
                for error in errors[:2]:  # Show first 2 errors
                    error_text_label = MDLabel(
                        text=f"  • {error}",
                        theme_text_color="Error",
                        font_size="12sp",
                        size_hint_y=None,
                        height=dp(20),
                        text_size=(dp(400), None)
                    )
                    card.add_widget(error_text_label)
            
            # Warnings
            warnings = validation.get('warnings', [])
            if warnings:
                warning_label = MDLabel(
                    text="⚠️ Warnings:",
                    theme_text_color="Secondary",
                    font_size="14sp",
                    size_hint_y=None,
                    height=dp(20)
                )
                card.add_widget(warning_label)
                
                for warning in warnings[:2]:  # Show first 2 warnings
                    warning_text_label = MDLabel(
                        text=f"  • {warning}",
                        theme_text_color="Secondary",
                        font_size="12sp",
                        size_hint_y=None,
                        height=dp(20),
                        text_size=(dp(400), None)
                    )
                    card.add_widget(warning_text_label)
            
            # Recommendations
            recommendations = validation.get('recommendations', [])
            if recommendations and not has_errors:
                rec_button = MDButton(
                    text=f"💡 {len(recommendations)} Recommendations Available",
                    size_hint=(None, None),
                    size=(dp(280), dp(36)),
                    on_release=lambda x: self.show_detailed_recommendations(recommendations)
                )
                card.add_widget(rec_button)
            
            return card
            
        except Exception as e:
            print(f"Error creating validation status card: {e}")
            return None

    def show_detailed_recommendations(self, recommendations):
        """Show detailed recommendations in a popup or detailed view"""
        try:
            # For now, show in toast - could be enhanced to show in popup
            rec_text = "; ".join(recommendations[:3])
            toast(f"Recommendations: {rec_text}")
        except Exception as e:
            print(f"Error showing recommendations: {e}")

    def update_tab_availability(self, available_analyses):
        """Update tab button availability based on validation"""
        try:
            # Define tab requirements
            tab_requirements = {
                'auto_detection': lambda analyses: True,  # Always available
                'descriptive': lambda analyses: 'descriptive' in analyses,
                'inferential': lambda analyses: 'inferential' in analyses,
                'qualitative': lambda analyses: 'qualitative' in analyses
            }
            
            # Update each tab button
            for tab_id, requirement_func in tab_requirements.items():
                button_id = f"{tab_id}_tab_btn"
                if hasattr(self.ids, button_id):
                    button = getattr(self.ids, button_id)
                    is_available = requirement_func(available_analyses)
                    
                    # Update button appearance based on availability
                    if is_available:
                        button.disabled = False
                        button.opacity = 1.0
                    else:
                        button.disabled = True
                        button.opacity = 0.5
                        
        except Exception as e:
            print(f"Error updating tab availability: {e}")

    def show_validation_error(self, error_message):
        """Show validation error in UI"""
        try:
            if hasattr(self.ids, 'tab_content_area'):
                content_area = self.ids.tab_content_area
                content_area.clear_widgets()
                
                error_label = MDLabel(
                    text=f"Validation Error: {error_message}",
                    theme_text_color="Error",
                    halign="center",
                    font_size="16sp"
                )
                content_area.add_widget(error_label)
        except Exception as e:
            print(f"Error showing validation error: {e}")

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
            app = App.get_running_app()
            primary_color = app.theme_cls.primary_color
            surface_color = getattr(app.theme_cls, 'surface_color', (0.98, 0.98, 0.98, 1))
            buttons = {
                'auto_detection_tab_btn': 'auto_detection',
                'descriptive_tab_btn': 'descriptive',
                'inferential_tab_btn': 'inferential',
                'qualitative_tab_btn': 'qualitative'
            }
            for btn_id, tab_name in buttons.items():
                if hasattr(self.ids, btn_id):
                    button = getattr(self.ids, btn_id)
                    if tab_name == self.current_tab:
                        button.md_bg_color = primary_color
                        button.text_color = (1, 1, 1, 1)  # White text
                    else:
                        button.md_bg_color = surface_color
                        button.text_color = (0, 0, 0, 1)  # Black text
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
        """Load auto-detection tab content with enhanced styling"""
        content_area = self.ids.tab_content_area
        
        # Add title with enhanced styling
        title_label = MDLabel(
            text="Auto-Detection Analysis",
            
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(56),
            halign="center"
        )
        content_area.add_widget(title_label)
        
        # Add description with better formatting
        desc_label = MDLabel(
            text="Automatically detect appropriate analysis methods based on your data characteristics and response patterns",
            halign="center",
            theme_text_color="Secondary",
            
            font_size="16sp",
            size_hint_y=None,
            height=dp(60),
            text_size=(None, None)
        )
        content_area.add_widget(desc_label)
        
        # Add run button with enhanced styling
        run_button = MDButton(
            text="Run Auto-Detection",
            style="elevated",
            size_hint=(None, None),
            size=(dp(240), dp(56)),
            pos_hint={"center_x": 0.5},
            radius=[8, 8, 8, 8],
            elevation=2,
            on_release=lambda x: self.load_auto_detection()
        )
        content_area.add_widget(run_button)
        
    def load_descriptive_content(self):
        """Load descriptive analysis tab content with enhanced styling"""
        content_area = self.ids.tab_content_area
        
        # Add title with enhanced styling
        title_label = MDLabel(
            text="Descriptive Analysis",
            
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(56),
            halign="center"
        )
        content_area.add_widget(title_label)
        
        # Add description with better formatting
        desc_label = MDLabel(
            text="Generate comprehensive descriptive statistics, frequency distributions, and data summaries for your survey responses",
            halign="center",
            theme_text_color="Secondary",
            
            font_size="16sp",
            size_hint_y=None,
            height=dp(60),
            text_size=(None, None)
        )
        content_area.add_widget(desc_label)
        
        # Add run button with enhanced styling
        run_button = MDButton(
            text="Run Descriptive Analysis",
            style="elevated",
            size_hint=(None, None),
            size=(dp(240), dp(56)),
            pos_hint={"center_x": 0.5},
            radius=[8, 8, 8, 8],
            elevation=2,
            on_release=lambda x: self.load_descriptive()
        )
        content_area.add_widget(run_button)
        
    def load_inferential_content(self):
        """Load inferential analysis tab content with enhanced styling"""
        content_area = self.ids.tab_content_area
        
        # Add title with enhanced styling
        title_label = MDLabel(
            text="Inferential Analysis",
            
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(56),
            halign="center"
        )
        content_area.add_widget(title_label)
        
        # Add description with better formatting
        desc_label = MDLabel(
            text="Perform statistical tests, hypothesis testing, and inferential analysis to draw conclusions from your survey data",
            halign="center",
            theme_text_color="Secondary",
            
            font_size="16sp",
            size_hint_y=None,
            height=dp(60),
            text_size=(None, None)
        )
        content_area.add_widget(desc_label)
        
        # Add run button with enhanced styling
        run_button = MDButton(
            text="Run Inferential Analysis",
            style="elevated",
            size_hint=(None, None),
            size=(dp(240), dp(56)),
            pos_hint={"center_x": 0.5},
            radius=[8, 8, 8, 8],
            elevation=2,
            on_release=lambda x: self.load_inferential()
        )
        content_area.add_widget(run_button)
        
    def load_qualitative_content(self):
        """Load qualitative analysis tab content with enhanced styling"""
        content_area = self.ids.tab_content_area
        
        # Add title with enhanced styling
        title_label = MDLabel(
            text="Qualitative Analysis",
            
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(56),
            halign="center"
        )
        content_area.add_widget(title_label)
        
        # Add description with better formatting
        desc_label = MDLabel(
            text="Analyze text responses, sentiment, themes, and qualitative data using advanced NLP and text analysis techniques",
            halign="center",
            theme_text_color="Secondary",
            
            font_size="16sp",
            size_hint_y=None,
            height=dp(60),
            text_size=(None, None)
        )
        content_area.add_widget(desc_label)
        
        # Add run button with enhanced styling
        run_button = MDButton(
            text="Run Qualitative Analysis",
            style="elevated",
            size_hint=(None, None),
            size=(dp(240), dp(56)),
            pos_hint={"center_x": 0.5},
            radius=[8, 8, 8, 8],
            elevation=2,
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
            # Use a grid layout for 3 cards per row (6 total cards)
            stats_container.cols = 3
            stat_items = [
                ("Total Responses", stats.get('total_responses', 0), "database", "Total responses collected"),
                ("Questions", stats.get('total_questions', 0), "help-circle", "Questions in this project"),
                ("Completion Rate", f"{stats.get('completion_rate', 0)}%", "check-circle", "Survey completion rate"),
                ("Respondents", stats.get('unique_respondents', 0), "account-group", "Unique respondents"),
                ("Data Quality", f"{stats.get('data_quality', 0)}%", "shield-check", "Non-empty responses"),
                ("Last Updated", stats.get('last_updated', 'Never'), "clock", "Most recent response"),
            ]
            from widgets.analytics_stat_card import AnalyticsStatCard
            for label, value, icon, note in stat_items:
                try:
                    card = AnalyticsStatCard(
                        title=label, 
                        value=str(value), 
                        icon=icon, 
                        note=note,
                        size_hint=(None, None),
                        size=(dp(200), dp(90))  # Enhanced size for better visibility
                    )
                    if card:
                        stats_container.add_widget(card)
                except Exception as card_error:
                    print(f"Error creating analytics stat card for {label}: {card_error}")
                    # Fallback to simple card if AnalyticsStatCard fails
                    self.create_fallback_stat_card(stats_container, label, value, icon, note)
        except Exception as e:
            print(f"Error updating quick stats: {e}")

    def get_project_stats(self):
        """Get comprehensive statistics for the current project"""
        if not self.current_project_id:
            return {}
            
        try:
            app = App.get_running_app()
            conn = app.db_service.get_db_connection()
            cursor = conn.cursor()
            
            # Get current user for filtering
            user_data = app.auth_service.get_user_data()
            user_id = user_data.get('id') if user_data else None
            
            if not user_id:
                print("No user_id available for analytics stats filtering")
                return {}
            
            print(f"Getting comprehensive stats for project {self.current_project_id} (user: {user_id})")
            
            # Get comprehensive project statistics in one query
            # Updated to use correct SQLite database structure
            cursor.execute("""
                SELECT 
                    COUNT(r.response_id) as total_responses,
                    COUNT(DISTINCT r.respondent_id) as unique_respondents,
                    COUNT(DISTINCT q.id) as total_questions,
                    MAX(r.collected_at) as last_response_date
                FROM responses r
                LEFT JOIN questions q ON r.project_id = q.project_id AND r.user_id = q.user_id
                WHERE r.project_id = ? AND r.user_id = ?
            """, (self.current_project_id, user_id))
            
            stats = cursor.fetchone()
            
            if not stats:
                return {}
            
            total_responses = stats['total_responses'] or 0
            unique_respondents = stats['unique_respondents'] or 0
            total_questions = stats['total_questions'] or 0
            last_response_date = stats['last_response_date']
            
            # Calculate completion rate more accurately
            completion_rate = 0
            if total_questions > 0 and unique_respondents > 0:
                expected_total = total_questions * unique_respondents
                completion_rate = min(100, (total_responses / expected_total) * 100) if expected_total > 0 else 0
            
            # Format last updated date
            last_updated = "Never"
            if last_response_date:
                try:
                    from datetime import datetime
                    if isinstance(last_response_date, str):
                        # Parse the date string
                        date_obj = datetime.fromisoformat(last_response_date.replace('Z', '+00:00'))
                        last_updated = date_obj.strftime("%Y-%m-%d %H:%M")
                    else:
                        last_updated = last_response_date.strftime("%Y-%m-%d %H:%M")
                except:
                    last_updated = str(last_response_date)
            
            # Get additional analytics data for data quality
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN response_value IS NOT NULL AND response_value != '' THEN 1 END) as non_empty_responses,
                    COUNT(*) as all_response_slots
                FROM responses 
                WHERE project_id = ? AND user_id = ?
            """, (self.current_project_id, user_id))
            
            quality_stats = cursor.fetchone()
            non_empty_responses = quality_stats['non_empty_responses'] if quality_stats else 0
            all_response_slots = quality_stats['all_response_slots'] if quality_stats else 0
            
            # Calculate data quality percentage
            data_quality = 0
            if all_response_slots > 0:
                data_quality = round((non_empty_responses / all_response_slots) * 100, 1)
            
            print(f"Analytics stats for project {self.current_project_id}: "
                  f"responses={total_responses}, questions={total_questions}, "
                  f"respondents={unique_respondents}, completion={completion_rate}%, "
                  f"quality={data_quality}%")
                
            return {
                'total_responses': total_responses,
                'total_questions': total_questions,
                'completion_rate': round(completion_rate, 1),
                'unique_respondents': unique_respondents,
                'data_quality': data_quality,
                'last_updated': last_updated
            }
            
        except Exception as e:
            print(f"Error getting project stats: {e}")
            import traceback
            traceback.print_exc()
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

    def create_fallback_stat_card(self, container, title, value, icon, note):
        """Create a fallback statistics card when AnalyticsStatCard is not available"""
        try:
            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel
            from kivymd.uix.boxlayout import MDBoxLayout
            
            card = MDCard(
                size_hint=(None, None),
                size=(dp(200), dp(90)),
                elevation=2,
                radius=[8, 8, 8, 8],
                padding=dp(12)
            )
            
            layout = MDBoxLayout(
                orientation='vertical',
                spacing=dp(8)
            )
            
            # Title with icon
            title_layout = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(8),
                size_hint_y=None,
                height=dp(24)
            )
            
            title_label = MDLabel(
                text=str(title).strip(),
                
                theme_text_color="Secondary",
                halign="left",
                size_hint_x=1
            )
            
            title_layout.add_widget(title_label)
            layout.add_widget(title_layout)
            
            # Value
            value_label = MDLabel(
                text=str(value).strip(),
                theme_text_color="Primary", 
                halign="center",
                size_hint_y=None,
                height=dp(32)
            )
            layout.add_widget(value_label)
            
            # Note
            note_label = MDLabel(
                text=str(note).strip(),
                
                theme_text_color="Secondary",
                halign="center",
                size_hint_y=None,
                height=dp(16)
            )
            layout.add_widget(note_label)
            
            card.add_widget(layout)
            container.add_widget(card)
            
        except Exception as e:
            print(f"Error creating fallback stat card: {e}")

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
                    
                    theme_text_color="Secondary",
                    halign="center",
                    size_hint_y=None,
                    height=dp(20)
                )
                
                value_label = MDLabel(
                    text=str(value).strip(),
                    
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
                # Check backend health first
                health = self.analytics_service.check_backend_health()
                if health.get('available', False):
                    print("Analytics backend is available")
                else:
                    print(f"Analytics backend unavailable: {health.get('error', 'Unknown error')}")
                
                recommendations = self.analytics_service.get_analysis_recommendations(
                    self.current_project_id
                )
                Clock.schedule_once(
                    lambda dt: self._display_auto_detection(recommendations), 0
                )
        except Exception as e:
            print(f"Error in auto-detection: {e}")
            import traceback
            traceback.print_exc()
            Clock.schedule_once(lambda dt: self.show_error(f"Auto-detection failed: {str(e)}"), 0)
        finally:
            Clock.schedule_once(lambda dt: self.set_loading(False), 0)

    def _display_auto_detection(self, recommendations):
        """Display auto-detection recommendations with enhanced formatting"""
        content_area = self.ids.tab_content_area
        content_area.clear_widgets()
        
        if not recommendations:
            self.show_no_recommendations_state()
            return
            
        # Format recommendations using service
        formatted_results = self.analytics_service.format_analysis_results_for_ui(
            recommendations, 'auto_detection'
        )
        
        # Display formatted results
        self.display_formatted_results(formatted_results)

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
                print(f"Starting descriptive analysis for project {self.current_project_id}")
                
                # Check backend availability
                if self.analytics_service.is_backend_available():
                    print("Using backend for descriptive analysis")
            else:
                    print("Backend unavailable, using local descriptive analysis")
                
                    results = self.analytics_service.run_descriptive_analysis(
                        self.current_project_id
                    )
                    Clock.schedule_once(
                        lambda dt: self._display_descriptive_results(results), 0
                    )
        except Exception as e:
            print(f"Error in descriptive analysis: {e}")
            import traceback
            traceback.print_exc()
            Clock.schedule_once(lambda dt: self.show_error(f"Descriptive analysis failed: {str(e)}"), 0)
        finally:
            Clock.schedule_once(lambda dt: self.set_loading(False), 0)

    def _display_descriptive_results(self, results):
        """Display descriptive analysis results with enhanced formatting"""
        content_area = self.ids.tab_content_area
        content_area.clear_widgets()
        
        if not results or 'error' in results:
            self.show_analysis_error(results.get('error', 'No results available'), 'descriptive')
            return
        
        # Format results using service
        formatted_results = self.analytics_service.format_analysis_results_for_ui(
            results, 'descriptive'
        )
        
        # Display formatted results
        self.display_formatted_results(formatted_results)

    def load_inferential(self):
        """Load inferential statistics"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
            
        self.set_loading(True)
        threading.Thread(target=self._load_inferential_thread, daemon=True).start()

    def _load_inferential_thread(self):
        """Background thread for inferential analytics"""
        try:
            if self.analytics_service:
                print(f"Starting inferential analysis for project {self.current_project_id}")
                
                # Try to run actual inferential analysis
                results = self.analytics_service.run_inferential_analysis(self.current_project_id)
                
                # If backend is not available, provide fallback message
                if 'error' in results:
                    results = {
                        'analysis_type': 'inferential',
                        'message': 'Inferential analysis is available when the analytics backend is running',
                        'available_tests': [
                            'T-tests for comparing means',
                            'ANOVA for multiple group comparisons',
                            'Chi-square tests for categorical data',
                            'Correlation significance tests',
                            'Regression analysis'
                        ]
                    }
                
                Clock.schedule_once(
                    lambda dt: self._display_inferential_results(results), 0
                )
        except Exception as e:
            print(f"Error in inferential analysis: {e}")
            import traceback
            traceback.print_exc()
            Clock.schedule_once(lambda dt: self.show_error(f"Inferential analysis failed: {str(e)}"), 0)
        finally:
            Clock.schedule_once(lambda dt: self.set_loading(False), 0)

    def _display_inferential_results(self, results):
        """Display inferential analysis results with enhanced formatting"""
        content_area = self.ids.tab_content_area
        content_area.clear_widgets()
        
        if not results or 'error' in results:
            self.show_analysis_error(results.get('error', 'No results available'), 'inferential')
            return
        
        # Format results using service
        formatted_results = self.analytics_service.format_analysis_results_for_ui(
            results, 'inferential'
        )
        
        # Display formatted results
        self.display_formatted_results(formatted_results)

    def load_qualitative(self):
        """Load qualitative analytics"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
            
        self.set_loading(True)
        threading.Thread(target=self._load_qualitative_thread, daemon=True).start()

    def _load_qualitative_thread(self):
        """Background thread for qualitative analytics"""
        try:
            if self.analytics_service:
                print(f"Starting qualitative analysis for project {self.current_project_id}")
                
                # Try to run actual qualitative analysis
                results = self.analytics_service.run_qualitative_analysis(self.current_project_id)
                
                # If backend is not available, provide fallback message
                if 'error' in results:
                    results = {
                        'analysis_type': 'qualitative',
                        'message': 'Qualitative analysis is available when the analytics backend is running',
                        'available_analyses': [
                            'Sentiment analysis of text responses',
                            'Word frequency analysis',
                            'Thematic analysis',
                            'Content categorization',
                            'Text similarity analysis'
                        ]
                    }
                
                Clock.schedule_once(
                    lambda dt: self._display_qualitative_results(results), 0
                )
        except Exception as e:
            print(f"Error in qualitative analysis: {e}")
            import traceback
            traceback.print_exc()
            Clock.schedule_once(lambda dt: self.show_error(f"Qualitative analysis failed: {str(e)}"), 0)
        finally:
            Clock.schedule_once(lambda dt: self.set_loading(False), 0)

    def _display_qualitative_results(self, results):
        """Display qualitative analysis results with enhanced formatting"""
        content_area = self.ids.tab_content_area
        content_area.clear_widgets()
        
        if not results or 'error' in results:
            self.show_analysis_error(results.get('error', 'No results available'), 'qualitative')
            return
        
        # Format results using service
        formatted_results = self.analytics_service.format_analysis_results_for_ui(
            results, 'qualitative'
        )
        
        # Display formatted results
        self.display_formatted_results(formatted_results)

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
        """Export analysis results with format selection"""
        if not self.analysis_results:
            toast("No results to export")
            return
            
        try:
            # Show export format selection
            toast("Choose export format: JSON, CSV, or Summary")
            # Could implement format selection dialog here
            
        except Exception as e:
            print(f"Error in export results: {e}")
            toast("Export preparation failed")

    def show_analysis_config(self):
        """Show analysis configuration dialog"""
        toast("Analysis configuration coming soon")
        
    def on_window_resize(self, window, width, height):
        self.update_responsive_layout()

    def update_responsive_layout(self):
        # Responsive layout for horizontal stat cards
        try:
            # Since we're using horizontal layout, we don't need to set columns
            # The cards will automatically flow horizontally
            if hasattr(self.ids, 'stats_container'):
                self.ids.stats_container.do_layout()
        except Exception as e:
            print(f"Error in analytics responsive layout: {e}")

    def display_formatted_results(self, formatted_results):
        """Display formatted analysis results using UI components"""
        content_area = self.ids.tab_content_area
        
        try:
            # Handle errors first
            if 'error' in formatted_results:
                self.show_analysis_error(formatted_results['error'], formatted_results.get('analysis_type', 'unknown'))
                return
            
            # Add timestamp header
            timestamp = formatted_results.get('timestamp', datetime.now().isoformat())
            timestamp_label = MDLabel(
                text=f"Analysis completed: {timestamp.split('T')[0]} {timestamp.split('T')[1][:8]}",
                theme_text_color="Secondary",
                font_size="12sp",
                size_hint_y=None,
                height=dp(24),
                halign="center"
            )
            content_area.add_widget(timestamp_label)
            
            # Display each UI component
            ui_components = formatted_results.get('ui_components', [])
            for component in ui_components:
                widget = self.create_result_widget(component)
                if widget:
                    content_area.add_widget(widget)
            
            # Add export and action buttons if we have results
            if ui_components:
                self.add_result_action_buttons(content_area, formatted_results)
            
        except Exception as e:
            print(f"Error displaying formatted results: {e}")
            self.show_analysis_error(f"Display error: {str(e)}", 'display')

    def add_result_action_buttons(self, content_area, formatted_results):
        """Add action buttons for results (export, config, help)"""
        try:
            from kivymd.uix.boxlayout import MDBoxLayout
            from kivymd.uix.button import MDButton
            from kivymd.uix.button import MDIconButton
            
            # Action buttons layout
            button_layout = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(16),
            size_hint_y=None,
            height=dp(48),
                padding=[dp(20), dp(16), dp(20), dp(16)]
            )
            
            # Export results button
            export_button = MDButton(
                text="📄 Export Results",
                size_hint_x=1,
                height=dp(40),
                radius=[6, 6, 6, 6],
                elevation=2,
                on_release=lambda x: self.export_current_results(formatted_results)
            )
            button_layout.add_widget(export_button)
            
            # Analysis config button
            config_button = MDButton(
                text="⚙️ Analysis Config",
                size_hint_x=1,
                height=dp(40),
                radius=[6, 6, 6, 6],
                elevation=2,
                on_release=lambda x: self.show_analysis_config()
            )
            button_layout.add_widget(config_button)
            
            # Help button
            help_button = MDIconButton(
                icon="help-circle",
                size_hint_x=None,
                width=dp(40),
                height=dp(40),
                theme_icon_color="Primary",
                on_release=lambda x: self.show_analysis_help()
            )
            button_layout.add_widget(help_button)
            
            content_area.add_widget(button_layout)
            
        except Exception as e:
            print(f"Error adding result action buttons: {e}")

    def show_analysis_help(self):
        """Show analysis help information"""
        try:
            analysis_type = self.current_tab
            help_messages = {
                'auto_detection': "Auto-Detection analyzes your data and recommends the best analysis methods based on data characteristics.",
                'descriptive': "Descriptive Analysis provides summary statistics, distributions, and basic data insights.",
                'inferential': "Inferential Analysis performs statistical tests to draw conclusions and test hypotheses.",
                'qualitative': "Qualitative Analysis examines text responses and categorical patterns in your data."
            }
            
            help_text = help_messages.get(analysis_type, "This analysis provides insights into your survey data.")
            toast(f"Help: {help_text}")
            
        except Exception as e:
            print(f"Error showing analysis help: {e}")
            toast("Analysis help: Use the tabs above to explore different types of analysis for your data.")

    def create_result_widget(self, component):
        """Create a widget based on component type"""
        try:
            component_type = component.get('type', 'unknown')
            
            if component_type == 'summary_card':
                return self.create_summary_card_widget(component)
            elif component_type == 'numeric_stats_card':
                return self.create_numeric_stats_widget(component)
            elif component_type == 'categorical_stats_card':
                return self.create_categorical_stats_widget(component)
            elif component_type == 'recommendation_card':
                return self.create_recommendation_widget(component)
            elif component_type == 'error_card':
                return self.create_error_widget(component)
            elif component_type == 'info_card':
                return self.create_info_widget(component)
            elif component_type == 'text_analysis_card':
                return self.create_text_analysis_widget(component)
            elif component_type == 'correlation_card':
                return self.create_correlation_widget(component)
            else:
                return self.create_generic_widget(component)
                
        except Exception as e:
            print(f"Error creating result widget: {e}")
            return None

    def create_summary_card_widget(self, component):
        """Create summary card widget"""
        try:
            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel
            from kivymd.uix.boxlayout import MDBoxLayout
            from kivy.uix.gridlayout import GridLayout
            
            card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(12),
                size_hint_y=None,
                height=dp(150),
                elevation=2
            )
            
            # Title
            title_label = MDLabel(
                text=component.get('title', 'Summary'),
                theme_text_color="Primary",
                font_size="18sp",
                size_hint_y=None,
                height=dp(32)
            )
            card.add_widget(title_label)
            
            # Metrics grid
            metrics_grid = GridLayout(
                cols=2,
                spacing=dp(8),
                size_hint_y=None,
                height=dp(80)
            )
            
            metrics = component.get('metrics', [])
            for metric in metrics[:4]:  # Show up to 4 metrics
                metric_layout = MDBoxLayout(
                    orientation='vertical',
                    spacing=dp(4)
                )
                
                metric_label = MDLabel(
                    text=metric.get('label', ''),
                    theme_text_color="Secondary",
                    font_size="12sp",
                    size_hint_y=None,
                    height=dp(16)
                )
                
                metric_value = MDLabel(
                    text=str(metric.get('value', '')),
            theme_text_color="Primary",
                    font_size="16sp",
            size_hint_y=None,
                    height=dp(24)
                )
                
                metric_layout.add_widget(metric_label)
                metric_layout.add_widget(metric_value)
                metrics_grid.add_widget(metric_layout)
            
            card.add_widget(metrics_grid)
            return card
            
        except Exception as e:
            print(f"Error creating summary card: {e}")
            return None

    def create_numeric_stats_widget(self, component):
        """Create numeric statistics widget"""
        try:
            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel
            from kivymd.uix.boxlayout import MDBoxLayout
            from kivy.uix.gridlayout import GridLayout
            
            card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(8),
                size_hint_y=None,
                height=dp(120),
                elevation=2
            )
            
            # Title
            title_label = MDLabel(
                text=component.get('title', 'Numeric Statistics'),
                theme_text_color="Primary",
                font_size="16sp",
                size_hint_y=None,
                height=dp(24)
            )
            card.add_widget(title_label)
            
            # Statistics
            statistics = component.get('statistics', {})
            stats_text = f"Mean: {statistics.get('mean', 0):.2f} | Median: {statistics.get('median', 0):.2f} | Std: {statistics.get('std', 0):.2f}"
            stats_label = MDLabel(
                text=stats_text,
                theme_text_color="Secondary",
                font_size="14sp",
                size_hint_y=None,
                height=dp(24)
            )
            card.add_widget(stats_label)
            
            range_text = f"Range: {statistics.get('min', 0):.2f} to {statistics.get('max', 0):.2f} | Count: {statistics.get('count', 0)}"
            range_label = MDLabel(
                text=range_text,
                theme_text_color="Secondary",
                font_size="14sp",
            size_hint_y=None,
                height=dp(24)
            )
            card.add_widget(range_label)
            
            return card
            
        except Exception as e:
            print(f"Error creating numeric stats widget: {e}")
            return None

    def create_categorical_stats_widget(self, component):
        """Create categorical statistics widget"""
        try:
            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel
            
            card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(8),
                size_hint_y=None,
                height=dp(120),
                elevation=2
            )
            
            # Title
            title_label = MDLabel(
                text=component.get('title', 'Categorical Statistics'),
                theme_text_color="Primary",
                font_size="16sp",
                size_hint_y=None,
                height=dp(24)
            )
            card.add_widget(title_label)
            
            # Statistics
            statistics = component.get('statistics', {})
            summary_text = f"Responses: {statistics.get('total_responses', 0)} | Unique: {statistics.get('unique_values', 0)}"
            summary_label = MDLabel(
                text=summary_text,
                theme_text_color="Secondary",
                font_size="14sp",
                size_hint_y=None,
                height=dp(24)
                )
            card.add_widget(summary_label)
            
            # Top categories
            top_categories = statistics.get('top_categories', [])
            if top_categories:
                categories_text = " | ".join([f"{cat}: {count}" for cat, count in top_categories[:3]])
                categories_label = MDLabel(
                    text=f"Top categories: {categories_text}",
                        theme_text_color="Secondary",
                        font_size="14sp",
                        size_hint_y=None,
                    height=dp(24)
                )
                card.add_widget(categories_label)
            
            return card
            
        except Exception as e:
            print(f"Error creating categorical stats widget: {e}")
            return None

    def create_recommendation_widget(self, component):
        """Create recommendation widget"""
        try:
            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel
            from kivymd.uix.button import MDButton
            
            # Color based on priority
            priority = component.get('priority', 'medium')
            if priority == 'high':
                card_color = (0.85, 0.95, 0.85, 1)  # Light green
            elif priority == 'medium':
                card_color = (0.95, 0.95, 0.85, 1)  # Light yellow
            else:
                card_color = (0.95, 0.95, 0.95, 1)  # Light gray
            
            card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(8),
                size_hint_y=None,
                height=dp(120),
                elevation=2,
                md_bg_color=card_color
            )
            
            # Title with priority indicator
            priority_icon = "🔥" if priority == 'high' else "⭐" if priority == 'medium' else "💡"
            title_label = MDLabel(
                text=f"{priority_icon} {component.get('title', 'Recommendation')}",
                theme_text_color="Primary",
                font_size="16sp",
                size_hint_y=None,
                height=dp(24)
            )
            card.add_widget(title_label)
            
            # Description
            description = component.get('description', 'No description available')
            desc_label = MDLabel(
                text=description,
                    theme_text_color="Secondary",
                font_size="14sp",
                size_hint_y=None,
                height=dp(48),
                text_size=(dp(300), None)
            )
            card.add_widget(desc_label)
            
            # Action button if available
            action = component.get('action', '')
            if action:
                action_button = MDButton(
                    text="Apply Recommendation",
                    size_hint=(None, None),
                    size=(dp(160), dp(32)),
                    on_release=lambda x: self.apply_recommendation(component)
                )
                card.add_widget(action_button)
            
            return card
            
        except Exception as e:
            print(f"Error creating recommendation widget: {e}")
            return None

    def create_error_widget(self, component):
        """Create error display widget"""
        try:
            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel
            from kivymd.uix.button import MDButton
            
            card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(8),
                size_hint_y=None,
                    height=dp(120),
                    elevation=2,
                    md_bg_color=(1, 0.95, 0.95, 1)  # Light red
                )
                
                # Title
            title_label = MDLabel(
                    text=f"❌ {component.get('title', 'Error')}",
                    theme_text_color="Error",
                    font_size="16sp",
                    size_hint_y=None,
                    height=dp(24)
                )
            card.add_widget(title_label)
            
            # Error message
            message = component.get('message', 'Unknown error occurred')
            message_label = MDLabel(
                text=message,
                theme_text_color="Error",
                font_size="14sp",
                size_hint_y=None,
                height=dp(48),
                text_size=(dp(300), None)
            )
            card.add_widget(message_label)
            
            # Help button
            help_button = MDButton(
                text="Get Help",
                size_hint=(None, None),
                size=(dp(120), dp(32)),
                on_release=lambda x: self.show_error_help(message)
            )
            card.add_widget(help_button)
        
            return card
        except Exception as e:
            print(f"Error creating error widget: {e}")
            return None

        

    def create_info_widget(self, component):
        """Create info display widget"""
        try:
            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel
            
            card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(8),
                size_hint_y=None,
                height=dp(100),
                elevation=2
            )
            
            # Title
            title_label = MDLabel(
                text=component.get('title', 'Information'),
                theme_text_color="Primary",
                font_size="16sp",
                size_hint_y=None,
                height=dp(24)
            )
            card.add_widget(title_label)
            
            # Items
            items = component.get('items', [])
            if items:
                items_text = ", ".join(items[:5])  # Show first 5 items
                items_label = MDLabel(
                    text=items_text,
                    theme_text_color="Secondary",
                    font_size="14sp",
                    size_hint_y=None,
                    height=dp(48),
                    text_size=(dp(300), None)
                )
                card.add_widget(items_label)
            
            return card
            
        except Exception as e:
            print(f"Error creating info widget: {e}")
            return None

    def create_text_analysis_widget(self, component):
        """Create text analysis widget"""
        try:
            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel
            
            card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(8),
                size_hint_y=None,
                height=dp(140),
                elevation=2
            )
        
        # Title
            title_label = MDLabel(
                text=component.get('title', 'Text Analysis'),
            theme_text_color="Primary",
                font_size="16sp",
            size_hint_y=None,
                height=dp(24)
            )
            card.add_widget(title_label)
            
            # Statistics
            statistics = component.get('statistics', {})
            stats_text = f"Responses: {statistics.get('response_count', 0)} | Avg Length: {statistics.get('average_length', 0):.1f} | Unique: {statistics.get('unique_responses', 0)}"
            stats_label = MDLabel(
                text=stats_text,
            theme_text_color="Secondary",
                font_size="14sp",
            size_hint_y=None,
                height=dp(24)
            )
            card.add_widget(stats_label)
            
            # Sample responses
            sample_responses = component.get('sample_responses', [])
            if sample_responses:
                sample_text = f"Sample: \"{sample_responses[0][:50]}...\""
                sample_label = MDLabel(
                    text=sample_text,
                    theme_text_color="Secondary",
                    font_size="12sp",
                    size_hint_y=None,
                    height=dp(48),
                    text_size=(dp(300), None)
                )
                card.add_widget(sample_label)
            
            return card
            
        except Exception as e:
            print(f"Error creating text analysis widget: {e}")
            return None

    def create_correlation_widget(self, component):
        """Create correlation analysis widget"""
        try:
            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel
            
            card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(8),
                size_hint_y=None,
                height=dp(100),
                elevation=2
            )
            
            # Title
            title_label = MDLabel(
                text=component.get('title', 'Correlation Analysis'),
                theme_text_color="Primary",
                font_size="16sp",
                size_hint_y=None,
                height=dp(24)
            )
            card.add_widget(title_label)
            
            # Correlation data summary
            data = component.get('data', {})
            if data:
                data_text = f"Correlation matrix calculated for {len(data)} variables"
                data_label = MDLabel(
                    text=data_text,
                    theme_text_color="Secondary",
                    font_size="14sp",
                    size_hint_y=None,
                    height=dp(24)
                )
                card.add_widget(data_label)
            
            return card
            
        except Exception as e:
            print(f"Error creating correlation widget: {e}")
            return None

    def create_generic_widget(self, component):
        """Create generic widget for unknown component types"""
        try:
            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel
            
            card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(8),
                size_hint_y=None,
                height=dp(80),
                elevation=2
            )
            
            # Title
            title_label = MDLabel(
                text=component.get('title', 'Analysis Result'),
                theme_text_color="Primary",
                font_size="16sp",
                size_hint_y=None,
                height=dp(24)
            )
            card.add_widget(title_label)
            
            # Generic content
            content = str(component.get('content', component))
            content_label = MDLabel(
                text=content[:100] + "..." if len(content) > 100 else content,
                theme_text_color="Secondary",
                font_size="14sp",
                size_hint_y=None,
                height=dp(32)
            )
            card.add_widget(content_label)
            
            return card
            
        except Exception as e:
            print(f"Error creating generic widget: {e}")
            return None

    def show_analysis_error(self, error_message, analysis_type):
        """Show detailed analysis error with troubleshooting information"""
        content_area = self.ids.tab_content_area
        content_area.clear_widgets()
        
        try:
            # Get detailed error information
            error_info = self.analytics_service.get_detailed_error_info(error_message, analysis_type)
            
            # Create comprehensive error display
            error_card = self.create_comprehensive_error_card(error_info, analysis_type)
            if error_card:
                content_area.add_widget(error_card)
                
        except Exception as e:
            print(f"Error showing analysis error: {e}")
            # Fallback to simple error display
            error_label = MDLabel(
                text=f"Analysis Error: {error_message}",
                theme_text_color="Error",
                halign="center",
                font_size="16sp"
            )
            content_area.add_widget(error_label)

    def create_comprehensive_error_card(self, error_info, analysis_type):
        """Create comprehensive error card with troubleshooting"""
        try:
            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel
            from kivymd.uix.button import MDButton
            from kivymd.uix.boxlayout import MDBoxLayout
            
            severity = error_info.get('severity', 'medium')
            error_type = error_info.get('type', 'unknown')
            
            # Color based on severity
            if severity == 'high':
                card_color = (1, 0.9, 0.9, 1)  # Light red
            elif severity == 'medium':
                card_color = (1, 0.95, 0.9, 1)  # Light orange
            else:
                card_color = (0.95, 0.95, 0.95, 1)  # Light gray
            
            card = MDCard(
                orientation="vertical",
                padding=dp(20),
                spacing=dp(12),
            size_hint_y=None,
                height=dp(300),
                elevation=3,
                md_bg_color=card_color
            )
            
            # Error header
            severity_icon = "🚨" if severity == 'high' else "⚠️" if severity == 'medium' else "ℹ️"
            header_label = MDLabel(
                text=f"{severity_icon} {analysis_type.title()} Analysis Error",
                theme_text_color="Error" if severity == 'high' else "Primary",
                font_size="18sp",
                size_hint_y=None,
                height=dp(32)
            )
            card.add_widget(header_label)
            
            # Error message
            error_message = error_info.get('error', 'Unknown error')
            error_label = MDLabel(
                text=error_message,
                theme_text_color="Error" if severity == 'high' else "Secondary",
                font_size="14sp",
            size_hint_y=None,
            height=dp(40),
                text_size=(dp(350), None)
            )
            card.add_widget(error_label)
            
            # Quick fixes
            quick_fixes = error_info.get('quick_fixes', [])
            if quick_fixes:
                fixes_label = MDLabel(
                    text="🔧 Quick Fixes:",
                theme_text_color="Primary",
                    font_size="16sp",
                size_hint_y=None,
                    height=dp(24)
                )
                card.add_widget(fixes_label)
                
                for fix in quick_fixes[:3]:
                    fix_label = MDLabel(
                        text=f"• {fix}",
                    theme_text_color="Secondary",
                        font_size="14sp",
                    size_hint_y=None,
                        height=dp(20)
                    )
                    card.add_widget(fix_label)
            
            # Action buttons
            button_layout = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(12),
                size_hint_y=None,
                height=dp(40)
            )
            
            # Retry button
            retry_button = MDButton(
                text="🔄 Retry",
                size_hint_x=1,
                height=dp(36),
                on_release=lambda x: self.retry_analysis(analysis_type)
            )
            button_layout.add_widget(retry_button)
            
            # Help button
            if error_info.get('need_help', False):
                help_button = MDButton(
                    text="❓ Get Help",
                    size_hint_x=1,
                    height=dp(36),
                    on_release=lambda x: self.show_detailed_troubleshooting(error_info)
                )
                button_layout.add_widget(help_button)
            
            # Data collection button for no-data errors
            if error_type == 'no_data':
                data_button = MDButton(
                    text="📊 Collect Data",
                    size_hint_x=1,
                    height=dp(36),
                    on_release=lambda x: self.go_to_data_collection()
                )
                button_layout.add_widget(data_button)
            
            card.add_widget(button_layout)
            
            return card
            
        except Exception as e:
            print(f"Error creating comprehensive error card: {e}")
            return None

    def show_no_recommendations_state(self):
        """Show state when no recommendations are available"""
        content_area = self.ids.tab_content_area
        
        no_rec_label = MDLabel(
            text="🤔 No specific recommendations available for this project.\n\nTry collecting more data or check data quality.",
            halign="center",
            theme_text_color="Secondary",
            font_size="16sp",
            text_size=(dp(300), None)
        )
        content_area.add_widget(no_rec_label)

    def apply_recommendation(self, recommendation):
        """Apply a recommendation"""
        try:
            method = recommendation.get('title', '')
            toast(f"Applying recommendation: {method}")
            # Could implement actual recommendation application logic here
        except Exception as e:
            print(f"Error applying recommendation: {e}")

    def show_error_help(self, error_message):
        """Show help for error"""
        try:
            error_info = self.analytics_service.get_detailed_error_info(error_message)
            troubleshooting = error_info.get('troubleshooting_steps', [])
            help_text = "\n".join(troubleshooting[:3])
            toast(f"Troubleshooting: {help_text}")
        except Exception as e:
            print(f"Error showing error help: {e}")

    def show_detailed_troubleshooting(self, error_info):
        """Show detailed troubleshooting information"""
        try:
            steps = error_info.get('troubleshooting_steps', [])
            troubleshooting_text = "\n".join(steps[:4])
            toast(f"Troubleshooting Steps:\n{troubleshooting_text}")
        except Exception as e:
            print(f"Error showing detailed troubleshooting: {e}")

    def retry_analysis(self, analysis_type):
        """Retry the analysis"""
        try:
            # Switch to the appropriate tab and reload
            self.current_tab = analysis_type
            self.update_tab_buttons()
            self.load_tab_content()
        except Exception as e:
            print(f"Error retrying analysis: {e}")
            toast("Retry failed")

    def export_current_results(self, formatted_results):
        """Export current analysis results"""
        try:
            export_data = formatted_results.get('export_data', {})
            if not export_data:
                toast("No data to export")
                return
                
            # For now, show export options
            toast("Export options: JSON, CSV, Summary")
            # Could implement actual export functionality here
            
        except Exception as e:
            print(f"Error exporting results: {e}")
            toast("Export failed")
