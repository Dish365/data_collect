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
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.boxlayout import MDBoxLayout

import threading
from datetime import datetime
from typing import Dict, List

#:kivy 2.0

Builder.load_file('kv/analytics.kv')

class AnalyticsTab(MDBoxLayout):
    """Base class for analytics tab content"""
    pass

class DataExplorationTab(AnalyticsTab):
    """Data exploration tab"""
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
    """Analytics Screen with declarative UI components"""
    
    # Properties
    current_project_id = StringProperty(None, allownone=True)
    current_project_name = StringProperty("")
    project_list = ListProperty([])
    project_map = {}
    
    # Analysis state
    is_loading = BooleanProperty(False)
    current_tab = StringProperty("auto_detection")
    analysis_results = ObjectProperty({})
    
    # Collapsible state
    is_project_overview_collapsed = BooleanProperty(False)
    
    # UI references
    project_menu = None
    analytics_service = None
    
    # UI constants
    CARD_HEIGHT = dp(400)
    PADDING = dp(24)
    SPACING = dp(20)
    BUTTON_HEIGHT = dp(48)
    ICON_SIZE = dp(32)
    FONT_SIZE = "16sp"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.analysis_results = {}
        Window.bind(on_resize=self.on_window_resize)
        
        # Detect if we're on a tablet
        self.is_tablet = self._detect_tablet()

    def _detect_tablet(self):
        """Detect if we're running on a tablet-sized device"""
        width = Window.width
        return 768 <= width <= 1366

    def _create_declarative_widget(self, widget_class_name, **properties):
        """Helper method to create declarative widgets from .kv definitions"""
        try:
            # Create widget using the class name defined in .kv
            widget_string = f'''
{widget_class_name}:
'''
            # Add properties if provided
            for key, value in properties.items():
                if isinstance(value, str):
                    widget_string += f'    {key}: "{value}"\\n'
                else:
                    widget_string += f'    {key}: {value}\\n'
            
            widget = Builder.load_string(widget_string)
            return widget
        except Exception as e:
            print(f"Error creating declarative widget {widget_class_name}: {e}")
            return None

    def on_enter(self):
        """Initialize analytics screen when entered"""
        Clock.schedule_once(self._delayed_init, 0.1)

    def _delayed_init(self, dt):
        """Delayed initialization"""
        if hasattr(self.ids, 'top_bar'):
            self.ids.top_bar.set_title("Analytics Dashboard")
            self.ids.top_bar.set_current_screen('analytics')
        
        self.setup_analytics_service()
        self.load_projects()
        self.setup_tabs()
        self.update_responsive_layout()
        self.update_quick_stats()
        self.update_project_overview_collapse_state()
        
        print(f"[DEBUG] _delayed_init - is_tablet: {self.is_tablet}, current_project_id: {self.current_project_id}")
        if self.is_tablet and not self.current_project_id:
            print(f"[DEBUG] Showing welcome state because no project selected")
            self.show_welcome_state()
        else:
            print(f"[DEBUG] Not showing welcome state - project already selected or not tablet")
        
        if self.current_project_id and hasattr(self, 'auto_detection_handler'):
            print(f"[DEBUG] Project already selected after init, triggering auto-detection")
            Clock.schedule_once(lambda dt: self.load_auto_detection(), 1.0)
        
        Clock.schedule_interval(self.check_active_tab, 1.0)

    def setup_analytics_service(self):
        """Initialize analytics service and handlers"""
        app = App.get_running_app()
        if not self.analytics_service:
            from services.analytics_service import AnalyticsService
            self.analytics_service = AnalyticsService(
                app.auth_service,
                app.db_service
            )
        
        print(f"[DEBUG] Initializing analytics handlers...")
        from services.auto_detection_analytics import AutoDetectionAnalyticsHandler
        from services.descriptive_analytics import DescriptiveAnalyticsHandler
        from services.qualitative_analytics import QualitativeAnalyticsHandler
        from services.data_exploration_service import DataExplorationService
        from services.categorical_analytics import CategoricalAnalyticsHandler
        from services.distribution_analytics import DistributionAnalyticsHandler
        
        self.data_exploration_handler = DataExplorationService(
            self.analytics_service, self
        )
        print(f"[DEBUG] Data exploration handler initialized")
        
        self.auto_detection_handler = AutoDetectionAnalyticsHandler(
            self.analytics_service, self
        )
        print(f"[DEBUG] Auto-detection handler initialized")
        
        self.descriptive_handler = DescriptiveAnalyticsHandler(
            self.analytics_service, self
        )
        print(f"[DEBUG] Descriptive handler initialized")
        
        self.qualitative_handler = QualitativeAnalyticsHandler(
            self.analytics_service, self
        )
        print(f"[DEBUG] Qualitative handler initialized")

        self.categorical_handler = CategoricalAnalyticsHandler(
            self.analytics_service, self
        )
        print(f"[DEBUG] Categorical handler initialized")

        self.distribution_handler = DistributionAnalyticsHandler(
            self.analytics_service, self
        )
        print(f"[DEBUG] Distribution handler initialized")

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
                self.show_no_projects_state()
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

    def show_no_projects_state(self):
        """Show message when no projects are available"""
        print(f"[DEBUG] show_no_projects_state called")
        
        content = self.get_tab_content('auto_detection')
        if content:
            content.clear_widgets()
            no_projects_card = self._create_declarative_widget('NoProjectsCard')
            if no_projects_card:
                content.add_widget(no_projects_card)
        else:
            print(f"[DEBUG] Could not get auto_detection content area for no projects state")

    def show_welcome_state(self):
        """Show welcome state"""
        print(f"[DEBUG] show_welcome_state called")
        print(f"[DEBUG] current_project_id when showing welcome: {self.current_project_id}")
        
        content = self.get_tab_content('auto_detection')
        if content:
            content.clear_widgets()
            welcome_card = self._create_declarative_widget('WelcomeCard')
            if welcome_card:
                content.add_widget(welcome_card)
        else:
            print(f"[DEBUG] Could not get auto_detection content area for welcome state")

    def show_select_project_message(self):
        """Show project selection message"""
        content = self.get_tab_content(self.current_tab)
        if content:
            content.clear_widgets()
            select_project_card = self._create_declarative_widget('SelectProjectCard')
            if select_project_card:
                content.add_widget(select_project_card)

    def show_loading_state(self, message="Analyzing your data..."):
        """Show loading state"""
        content = self.get_tab_content(self.current_tab)
        if content:
            content.clear_widgets()
            loading_card = self._create_declarative_widget('AnalyticsLoadingCard', loading_text=message)
            if loading_card:
                content.add_widget(loading_card)

    def show_error_state(self, title="Error", message="An error occurred"):
        """Show error state"""
        content = self.get_tab_content(self.current_tab)
        if content:
            content.clear_widgets()
            error_card = self._create_declarative_widget('ErrorCard', 
                                                       error_title=title, 
                                                       error_message=message)
            if error_card:
                content.add_widget(error_card)

    def show_coming_soon_state(self, title="Coming Soon", description="This feature is under development.", icon="flask-outline"):
        """Show coming soon state"""
        content = self.get_tab_content(self.current_tab)
        if content:
            content.clear_widgets()
            coming_soon_card = self._create_declarative_widget('ComingSoonCard',
                                                             feature_title=title,
                                                             feature_description=description,
                                                             feature_icon=icon)
            if coming_soon_card:
                content.add_widget(coming_soon_card)

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
        self.load_project_data_characteristics()
        
        print(f"[DEBUG] select_project - current_tab: {self.current_tab}")
        print(f"[DEBUG] select_project - has _auto_analysis_run: {hasattr(self, '_auto_analysis_run')}")
        
        if self.current_tab == "auto_detection":
            print(f"[DEBUG] select_project - triggering auto-detection analysis (on auto-detection tab)")
            toast(f"Analyzing {project['name']}...")
            Clock.schedule_once(lambda dt: self.load_auto_detection(), 0.5)
            self._auto_analysis_run = True
        else:
            print(f"[DEBUG] select_project - NOT triggering auto-detection (current_tab: {self.current_tab}) - just loading tab content")
            Clock.schedule_once(lambda dt: self.load_tab_content(), 0.2)
        
        toast(f"Selected: {project['name']}")

    def setup_tabs(self):
        """Setup analytics tabs"""
        if not hasattr(self.ids, 'analytics_tabs'):
            print(f"[DEBUG] ERROR: analytics_tabs not found in ids")
            return
            
        tabs = self.ids.analytics_tabs
        
        try:
            tabs.unbind(on_tab_selected=self.on_tab_switch)
        except:
            pass
        tabs.bind(on_tab_selected=self.on_tab_switch)
        
        print(f"[DEBUG] Analytics tabs setup complete")

    def on_tab_switch(self, tabs_primary, tab_item):
        """Handle tab switching"""
        print(f"[DEBUG] on_tab_switch called with tab_item: {tab_item}")
        
        # Get the tab text from the MDTabsItemText child
        tab_text = ""
        if hasattr(tab_item, 'children'):
            for child in tab_item.children:
                if hasattr(child, 'text'):
                    tab_text = child.text
                    break
        
        print(f"[DEBUG] tab_text extracted: '{tab_text}'")
        
        tab_map = {
            "Explore Data": "data_exploration",
            "Auto-Detection": "auto_detection",
            "Descriptive": "descriptive", 
            "Inferential": "inferential",
            "Qualitative": "qualitative"
        }
        
        new_tab = tab_map.get(tab_text, "auto_detection")
        self.switch_to_tab(new_tab)
        
        toast(f"Switched to {tab_text} Analytics")
    
    def switch_to_tab(self, tab_name: str):
        """Unified method to switch to a specific tab"""
        print(f"[DEBUG] switch_to_tab called for: {tab_name}")
        
        valid_tabs = ["data_exploration", "auto_detection", "descriptive", "inferential", "qualitative"]
        if tab_name not in valid_tabs:
            print(f"[DEBUG] Invalid tab name: {tab_name}")
            return
        
        old_tab = self.current_tab
        self.current_tab = tab_name
        print(f"[DEBUG] Switched from '{old_tab}' to '{self.current_tab}'")
        
        if self.current_project_id:
            print(f"[DEBUG] Loading content for switched tab: {self.current_tab}")
            self.load_tab_content()
        else:
            print(f"[DEBUG] No project selected for tab switch")
    
    def check_active_tab(self, dt):
        """Periodically check which tab is active and load content if needed"""
        if not self.current_project_id or not hasattr(self.ids, 'analytics_tabs'):
            return
        
        try:
            tabs = self.ids.analytics_tabs
            
            # In KivyMD 2.0, we need to check the current_item property
            if hasattr(tabs, 'current_item') and tabs.current_item:
                current_tab_item = tabs.current_item
                
                # Get the tab text from the MDTabsItemText child
                tab_text = None
                if hasattr(current_tab_item, 'children'):
                    for child in current_tab_item.children:
                        if hasattr(child, 'text'):
                            tab_text = child.text
                            break
                
                if tab_text:
                    tab_map = {
                        "Explore Data": "data_exploration",
                        "Auto-Detection": "auto_detection",
                        "Descriptive": "descriptive", 
                        "Inferential": "inferential",
                        "Qualitative": "qualitative"
                    }
                    
                    detected_tab = tab_map.get(tab_text, "auto_detection")
                    
                    if detected_tab != self.current_tab:
                        print(f"[DEBUG] check_active_tab detected tab change: '{self.current_tab}' -> '{detected_tab}'")
                        self.switch_to_tab(detected_tab)
                        
                        Clock.unschedule(self.check_active_tab)
                        Clock.schedule_interval(self.check_active_tab, 2.0)
                        return
        
        except Exception as e:
            print(f"[DEBUG] Error in check_active_tab: {e}")

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

    # Analysis methods
    def load_data_exploration(self):
        """Load data exploration"""
        print(f"[DEBUG] load_data_exploration called")
        print(f"[DEBUG] current_project_id: {self.current_project_id}")
        print(f"[DEBUG] has data_exploration_handler: {hasattr(self, 'data_exploration_handler')}")
        
        if not self.current_project_id:
            print(f"[DEBUG] No project selected, showing message")
            self.show_select_project_message()
            return
        
        if hasattr(self, 'data_exploration_handler'):
            print(f"[DEBUG] Calling data_exploration_handler.explore_project_data")
            toast("Loading data exploration...")
            self.data_exploration_handler.explore_project_data(self.current_project_id)
        else:
            print(f"[DEBUG] ERROR: Data exploration handler not available")
            toast("Data exploration handler not available")

    def load_auto_detection(self):
        """Load auto-detection"""
        print(f"[DEBUG] load_auto_detection called")
        print(f"[DEBUG] current_project_id: {self.current_project_id}")
        print(f"[DEBUG] has auto_detection_handler: {hasattr(self, 'auto_detection_handler')}")
        
        if not self.current_project_id:
            print(f"[DEBUG] No project ID, showing welcome state")
            self.show_welcome_state()
            return
        
        if hasattr(self, 'auto_detection_handler'):
            print(f"[DEBUG] Calling auto_detection_handler.run_auto_detection")
            toast("Running intelligent data analysis...")
            self.auto_detection_handler.run_auto_detection(self.current_project_id)
        else:
            print(f"[DEBUG] ERROR: Auto-detection handler not available")
            toast("Auto-detection handler not available")

    def load_descriptive(self):
        """Load descriptive analytics"""
        print(f"[DEBUG] load_descriptive called")
        print(f"[DEBUG] current_project_id: {self.current_project_id}")
        print(f"[DEBUG] has descriptive_handler: {hasattr(self, 'descriptive_handler')}")
        
        if not self.current_project_id:
            print(f"[DEBUG] No project selected, showing message")
            self.show_select_project_message()
            return
        
        if hasattr(self, 'descriptive_handler'):
            print(f"[DEBUG] Calling descriptive_handler.run_descriptive_analysis")
            toast("Loading descriptive analytics selection...")
            self.descriptive_handler.run_descriptive_analysis(self.current_project_id)
        else:
            print(f"[DEBUG] ERROR: Descriptive analytics handler not available")
            toast("Descriptive analytics handler not available")

    def load_qualitative(self):
        """Load qualitative analytics"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
        
        if hasattr(self, 'qualitative_handler'):
            toast("Analyzing text and qualitative data...")
            self.qualitative_handler.run_text_analysis(self.current_project_id)
        else:
            toast("Qualitative analytics handler not available")

    def load_inferential(self):
        """Load inferential statistics"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
        
        # Show coming soon state for inferential statistics
        inferential_description = """Advanced Statistical Inference - Coming Soon!

This powerful module will include:

• Hypothesis Testing
  - t-tests, chi-square tests, ANOVA  
  - Statistical significance testing
• Regression Analysis  
  - Linear and logistic regression
  - Multiple regression models

• Advanced Methods
  - Confidence intervals and p-values
  - Effect size calculations
  - Power analysis

Stay tuned for these advanced analytics capabilities!"""
        
        self.show_coming_soon_state(
            title="Inferential Statistics",
            description=inferential_description,
            icon="flask-outline"
        )

    def load_tab_content(self):
        """Load content for current tab"""
        print(f"[DEBUG] load_tab_content called for tab: {self.current_tab}")
        
        if not self.current_project_id:
            print(f"[DEBUG] No project ID available for loading tab content")
            return
            
        if self.current_tab == "data_exploration":
            print(f"[DEBUG] Loading data exploration content")
            self.load_data_exploration()
        elif self.current_tab == "auto_detection":
            print(f"[DEBUG] Loading auto-detection content")
            self.load_auto_detection()
        elif self.current_tab == "descriptive":
            print(f"[DEBUG] Loading descriptive content")
            self.load_descriptive()
        elif self.current_tab == "inferential":
            print(f"[DEBUG] Loading inferential content")
            self.load_inferential()
        elif self.current_tab == "qualitative":
            print(f"[DEBUG] Loading qualitative content")
            self.load_qualitative()
        else:
            print(f"[DEBUG] Unknown tab: {self.current_tab}")

    def load_project_data_characteristics(self):
        """Load project data characteristics"""
        pass
    
    def get_tab_content(self, tab_name):
        """Helper method to get content area for a specific tab"""
        print(f"[DEBUG] get_tab_content called for: {tab_name}")
        try:
            if not hasattr(self.ids, 'analytics_tabs'):
                print(f"[DEBUG] No analytics_tabs found")
                return None
                
            tabs = self.ids.analytics_tabs
            print(f"[DEBUG] Found analytics_tabs")
            
            # Look for the tabs_carousel in the tabs
            carousel = None
            if hasattr(tabs, 'ids') and 'tabs_carousel' in tabs.ids:
                carousel = tabs.ids.tabs_carousel
                print(f"[DEBUG] Found tabs_carousel in tabs.ids")
            else:
                # Search for the carousel in the tabs widget tree
                carousel = self._find_widget_by_id(tabs, 'tabs_carousel')
                if carousel:
                    print(f"[DEBUG] Found tabs_carousel in widget tree search")
            
            if not carousel:
                print(f"[DEBUG] Could not find tabs_carousel")
                return None
            
            tab_content_map = {
                'data_exploration': 'data_exploration_content',
                'auto_detection': 'auto_detection_content',
                'descriptive': 'descriptive_content', 
                'inferential': 'inferential_content',
                'qualitative': 'qualitative_content'
            }
            
            content_id = tab_content_map.get(tab_name)
            if not content_id:
                print(f"[DEBUG] Unknown tab name: {tab_name}")
                return None
            
            print(f"[DEBUG] Looking for content_id: {content_id}")
            
            # Search in the carousel's children (slides)
            if hasattr(carousel, 'children'):
                print(f"[DEBUG] Searching {len(carousel.children)} carousel slides")
                for i, slide in enumerate(carousel.children):
                    print(f"[DEBUG] Checking slide {i}: {type(slide).__name__}")
                    if hasattr(slide, 'ids') and content_id in slide.ids:
                        content = slide.ids[content_id]
                        print(f"[DEBUG] Found {content_id} in slide {i} ids!")
                        return content
                    
                    # Check if the slide itself has the target ID
                    if hasattr(slide, 'id') and slide.id == content_id:
                        print(f"[DEBUG] Slide {i} itself is the target content!")
                        return slide
                    
                    # Deep search in the slide's widget tree
                    content = self._find_widget_by_id(slide, content_id)
                    if content:
                        print(f"[DEBUG] Found {content_id} in slide {i} widget tree, type: {type(content)}")
                        return content
            
            print(f"[DEBUG] Could not find {content_id} in any carousel slide")
            return None
            
        except Exception as e:
            print(f"[DEBUG] Error in get_tab_content: {e}")
            import traceback
            print(f"[DEBUG] Traceback: {traceback.format_exc()}")
            return None
    
    def _find_widget_by_id(self, widget, target_id, depth=0):
        """Recursively search for a widget with the given ID"""
        indent = "  " * depth
        try:
            widget_type = type(widget).__name__
            
            widget_id = None
            if hasattr(widget, 'id'):
                widget_id = widget.id
            elif hasattr(widget, '_id'):
                widget_id = widget._id
            
            print(f"[DEBUG] {indent}Checking widget: {widget_type} (id: {widget_id})")
            
            if hasattr(widget, 'ids') and widget.ids:
                print(f"[DEBUG] {indent}Available IDs: {list(widget.ids.keys())}")
            
            if hasattr(widget, 'ids') and target_id in widget.ids:
                print(f"[DEBUG] {indent}Found {target_id} in widget's ids!")
                return widget.ids[target_id]
            
            if widget_id == target_id:
                print(f"[DEBUG] {indent}Widget itself has target ID!")
                return widget
            
            if hasattr(widget, 'children') and depth < 10:
                print(f"[DEBUG] {indent}Searching {len(widget.children)} children...")
                for i, child in enumerate(widget.children):
                    print(f"[DEBUG] {indent}Child {i}: {type(child).__name__}")
                    result = self._find_widget_by_id(child, target_id, depth + 1)
                    if result:
                        return result
            elif depth >= 10:
                print(f"[DEBUG] {indent}Max depth reached, stopping search")
            
            return None
        except Exception as e:
            print(f"[DEBUG] Error in _find_widget_by_id: {e}")
            return None

    # Callback methods for declarative UI components
    def show_project_selection_guide(self):
        """Show project selection guide"""
        toast("Tap the project dropdown above to select a project for analysis")

    def navigate_to_projects(self):
        """Navigate to projects screen"""
        toast("Navigate to Projects tab to create your first project")

    def show_backend_help(self):
        """Show backend setup help"""
        toast("Check the documentation for backend setup instructions")

    def request_early_access(self):
        """Request early access to inferential statistics"""
        toast("Early access request noted! We'll notify you when available.")

    def set_loading(self, loading):
        """Set loading state"""
        self.is_loading = loading
        if hasattr(self.ids, 'loading_spinner'):
            self.ids.loading_spinner.active = loading
        
        if loading:
            toast("Processing...")

    def show_error(self, message):
        """Show error message"""
        toast(f"Error: {message}")

    def refresh_analysis(self):
        """Refresh current analysis"""
        if self.current_project_id:
            toast("Refreshing analysis...")
            self.load_tab_content()
        else:
            toast("Select a project first to refresh analysis")

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