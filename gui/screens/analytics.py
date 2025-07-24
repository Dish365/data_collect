from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.scrollview import MDScrollView
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from widgets.top_bar import TopBar

import threading
from datetime import datetime

Builder.load_file('kv/analytics.kv')

class AnalyticsTab(MDBoxLayout, MDTabsBase):
    """Base class for analytics tab content - Tablet Optimized"""
    pass

class DataExplorationTab(AnalyticsTab):
    """Data exploration tab - Tablet Optimized"""
    pass

class AutoDetectionTab(AnalyticsTab):
    """Auto-detection and overview tab - Tablet Optimized"""
    pass

class DescriptiveTab(AnalyticsTab):
    """Descriptive analytics tab - Tablet Optimized"""
    pass

class InferentialTab(AnalyticsTab):
    """Inferential statistics tab - Tablet Optimized"""
    pass

class QualitativeTab(AnalyticsTab):
    """Qualitative analytics tab - Tablet Optimized"""
    pass

class AnalyticsScreen(Screen):
    """Analytics Screen optimized for Medium Tablets (9-11 inches)"""
    
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
    
    # Tablet-specific UI constants
    TABLET_CARD_HEIGHT = dp(400)  # Increased from dp(330) to dp(400) for larger overview area
    TABLET_PADDING = dp(24)
    TABLET_SPACING = dp(20)
    TABLET_BUTTON_HEIGHT = dp(48)
    TABLET_ICON_SIZE = dp(32)
    TABLET_FONT_SIZE = "16sp"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.analysis_results = {}
        Window.bind(on_resize=self.on_window_resize)
        
        # Detect if we're on a tablet
        self.is_tablet = self._detect_tablet()

    def _detect_tablet(self):
        """Detect if we're running on a tablet-sized device"""
        # Assume tablet if screen width is between 768-1366px (typical tablet range)
        width = Window.width
        return 768 <= width <= 1366

    def on_enter(self):
        """Initialize analytics screen when entered"""
        Clock.schedule_once(self._delayed_init, 0.1)

    def _delayed_init(self, dt):
        """Delayed initialization optimized for tablets"""
        # Set top bar title with tablet-appropriate styling
        if hasattr(self.ids, 'top_bar'):
            self.ids.top_bar.set_title("Analytics Dashboard")
            self.ids.top_bar.set_current_screen('analytics')
        
        self.setup_analytics_service()
        self.load_projects()
        self.setup_tablet_optimized_tabs()
        self.update_responsive_layout()
        self.update_tablet_quick_stats()
        
        # Show welcome message for tablets
        print(f"[DEBUG] _delayed_init - is_tablet: {self.is_tablet}, current_project_id: {self.current_project_id}")
        if self.is_tablet and not self.current_project_id:
            print(f"[DEBUG] Showing welcome state because no project selected")
            self.show_tablet_welcome_state()
        else:
            print(f"[DEBUG] Not showing welcome state - project already selected or not tablet")
        
        # If a project is already selected, trigger auto-detection analysis
        if self.current_project_id and hasattr(self, 'auto_detection_handler'):
            print(f"[DEBUG] Project already selected after init, triggering auto-detection")
            Clock.schedule_once(lambda dt: self.load_auto_detection(), 1.0)  # Longer delay to ensure everything is ready
        
        # Schedule a periodic check for tab changes (fallback mechanism)
        Clock.schedule_interval(self.check_active_tab, 1.0)

    def setup_analytics_service(self):
        """Initialize analytics service and tablet-optimized handlers"""
        app = App.get_running_app()
        if not self.analytics_service:
            from services.analytics_service import AnalyticsService
            self.analytics_service = AnalyticsService(
                app.auth_service,
                app.db_service
            )
        
        # Initialize tablet-optimized analytics handlers
        print(f"[DEBUG] Initializing analytics handlers...")
        from services.auto_detection_analytics import AutoDetectionAnalyticsHandler
        from services.descriptive_analytics import DescriptiveAnalyticsHandler
        from services.qualitative_analytics import QualitativeAnalyticsHandler
        from services.data_exploration_service import DataExplorationService
        
        # Initialize handlers with tablet awareness
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

    def load_projects(self):
        """Load available projects with tablet-optimized presentation"""
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
                self.show_tablet_no_projects_state()
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
            
            # Update project selector with tablet-friendly text
            if hasattr(self.ids, 'project_selector'):
                self.ids.project_selector.text = "Select Project for Analysis"
                self.ids.project_selector.font_size = self.TABLET_FONT_SIZE
                
        except Exception as e:
            print(f"Error loading projects: {e}")
            toast("❌ Error loading projects")
        finally:
            if conn:
                conn.close()

    def show_tablet_no_projects_state(self):
        """Show tablet-optimized message when no projects are available"""
        print(f"[DEBUG] show_tablet_no_projects_state called")
        
        # Use the helper method to get the content area
        content = self.get_tab_content('auto_detection')
        if content:
            content.clear_widgets()
            
            no_projects_card = self.create_tablet_empty_state_card(
                title="Welcome to Analytics!",
                message="To get started with data analysis:\n\n" +
                        "1.  Create a new project in the Projects tab\n" +
                        "2.  Add some survey questions\n" +
                        "3.  Collect responses from participants\n" +
                        "4.  Return here for powerful analytics insights!",
                icon="chart-line",  # Updated to use consistent icon
                action_text="Go to Projects",
                action_callback=lambda: self.navigate_to_projects()
            )
            content.add_widget(no_projects_card)
        else:
            print(f"[DEBUG] Could not get auto_detection content area for no projects state")

    def show_tablet_welcome_state(self):
        """Show tablet-optimized welcome state"""
        print(f"[DEBUG] show_tablet_welcome_state called")
        print(f"[DEBUG] current_project_id when showing welcome: {self.current_project_id}")
        
        # Use the helper method to get the content area
        content = self.get_tab_content('auto_detection')
        if content:
            content.clear_widgets()
            
            welcome_card = self.create_tablet_empty_state_card(
                title="Analytics Dashboard",
                message="Welcome to your data analytics workspace!\n\n" +
                        f"You have {len(self.project_list)} project(s) available.\n" +
                        "Select a project above to begin analyzing your data.",
                icon="lightbulb-outline",  # Updated to use outline version
                action_text="Show Project Guide",
                action_callback=lambda: self.show_project_selection_guide()
            )
            content.add_widget(welcome_card)
        else:
            print(f"[DEBUG] Could not get auto_detection content area for welcome state")

    def open_project_menu(self):
        """Open tablet-optimized project selection dropdown menu"""
        if self.project_menu:
            self.project_menu.dismiss()
            
        if not self.project_list:
            toast("No projects available")
            return
            
        menu_items = []
        for project in self.project_list:
            # Enhanced menu item text for tablets
            item_text = f"{project['name']}\n" + \
                       f"{project['response_count']} responses • " + \
                       f"{project['respondent_count']} respondents"
            
            menu_items.append({
                "text": item_text,
                "viewclass": "TwoLineListItem",
                "height": dp(72),  # Larger height for tablets
                "font_size": self.TABLET_FONT_SIZE,
                "on_release": lambda x=project: self.select_project(x)
            })
            
        self.project_menu = MDDropdownMenu(
            caller=self.ids.project_selector,
            items=menu_items,
            width_mult=5,  # Wider for tablets
            max_height=dp(400)  # Limit height on tablets
        )
        self.project_menu.open()

    def select_project(self, project):
        """Select a project with tablet-optimized feedback"""
        if self.project_menu:
            self.project_menu.dismiss()
            
        self.current_project_id = project['id']
        self.current_project_name = project['name']
        
        # Update project selector with enhanced text for tablets
        if hasattr(self.ids, 'project_selector'):
            selector_text = f"{project['name']}"
            if project['response_count'] > 0:
                selector_text += f" ({project['response_count']} responses)"
            self.ids.project_selector.text = selector_text
        
        # Update stats and characteristics
        self.update_tablet_quick_stats()
        self.load_project_data_characteristics()
        
        # Only auto-run analysis if we're specifically on the auto-detection tab
        print(f"[DEBUG] select_project - current_tab: {self.current_tab}")
        print(f"[DEBUG] select_project - has _auto_analysis_run: {hasattr(self, '_auto_analysis_run')}")
        
        # FIXED: Only trigger auto-detection if actually on auto-detection tab
        if self.current_tab == "auto_detection":
            print(f"[DEBUG] select_project - triggering auto-detection analysis (on auto-detection tab)")
            toast(f" Analyzing {project['name']}...")
            Clock.schedule_once(lambda dt: self.load_auto_detection(), 0.5)
            self._auto_analysis_run = True
        else:
            print(f"[DEBUG] select_project - NOT triggering auto-detection (current_tab: {self.current_tab}) - just loading tab content")
            # Just load the current tab content without auto-detection
            Clock.schedule_once(lambda dt: self.load_tab_content(), 0.2)
        
        toast(f" Selected: {project['name']}")

    def setup_tablet_optimized_tabs(self):
        """Setup analytics tabs optimized for tablets"""
        print(f"[DEBUG] Setting up tablet optimized tabs")
        if not hasattr(self.ids, 'analytics_tabs'):
            print(f"[DEBUG] ERROR: analytics_tabs not found in ids")
            print(f"[DEBUG] Available IDs: {list(self.ids.keys())}")
            return
            
        tabs = self.ids.analytics_tabs
        print(f"[DEBUG] Found analytics_tabs, type: {type(tabs)}")
        
        # Clear any existing bindings and bind the tab switch event
        try:
            tabs.unbind(on_tab_switch=self.on_tab_switch)
        except:
            pass
        tabs.bind(on_tab_switch=self.on_tab_switch)
        print(f"[DEBUG] Bound on_tab_switch event")
        
        # Also bind to the current_tab property change
        if hasattr(tabs, 'current_tab'):
            try:
                tabs.unbind(current_tab=self.on_current_tab_change)
            except:
                pass
            tabs.bind(current_tab=self.on_current_tab_change)
            print(f"[DEBUG] Bound current_tab property change")
        
        # Check if tabs have content areas
        tab_list = tabs.get_tab_list()
        print(f"[DEBUG] Number of tabs: {len(tab_list)}")
        for i, tab in enumerate(tab_list):
            print(f"[DEBUG] Tab {i}: {tab.title if hasattr(tab, 'title') else 'No title'}")
            print(f"[DEBUG] Tab {i} children count: {len(tab.children) if hasattr(tab, 'children') else 'No children'}")
        
        # Enhance tab appearance for tablets
        tab_list = tabs.get_tab_list()
        for i, tab in enumerate(tab_list):
            print(f"[DEBUG] Processing tab {i}: {tab}")
            if hasattr(tab, 'title'):
                original_title = tab.title
                print(f"[DEBUG] Tab {i} original title: '{original_title}'")
                # Add emoji prefixes to tab titles for better visual hierarchy
                title_map = {
                    "Auto-Detection": " Auto-Detection",
                    "Descriptive": " Descriptive", 
                    "Inferential": " Inferential",
                    "Qualitative": " Qualitative"
                }
                if original_title in title_map:
                    tab.title = title_map[original_title]
                    print(f"[DEBUG] Tab {i} new title: '{tab.title}'")
                else:
                    print(f"[DEBUG] Tab {i} title '{original_title}' not in title_map")
            else:
                print(f"[DEBUG] Tab {i} has no title attribute")
                # Try to find title through other means
                if hasattr(tab, 'text'):
                    print(f"[DEBUG] Tab {i} has text: '{tab.text}'")
                if hasattr(tab, 'tab_label'):
                    print(f"[DEBUG] Tab {i} has tab_label: {tab.tab_label}")
                    if hasattr(tab.tab_label, 'text'):
                        print(f"[DEBUG] Tab {i} tab_label.text: '{tab.tab_label.text}'")

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        """Handle tab switching with tablet optimizations"""
        print(f"[DEBUG] on_tab_switch called with tab_text: '{tab_text}'")
        
        # Clean up the tab text - remove KivyMD formatting and emojis
        clean_tab_text = tab_text
        
        # Remove KivyMD font formatting
        if '[/font]' in clean_tab_text:
            clean_tab_text = clean_tab_text.split('[/font]')[-1].strip()
        
        
        if ' ' in clean_tab_text:
            parts = clean_tab_text.split(' ')
            # Find the actual text part (not emoji)
            for part in parts:
                if part and not any(ord(char) > 127 for char in part):  # ASCII text only
                    clean_tab_text = part
                    break
        
        print(f"[DEBUG] clean_tab_text after processing: '{clean_tab_text}'")
        
        tab_map = {
            "Explore": "data_exploration",
            "Auto-Detection": "auto_detection",
            "Descriptive": "descriptive", 
            "Inferential": "inferential",
            "Qualitative": "qualitative"
        }
        
        old_tab = self.current_tab
        self.current_tab = tab_map.get(clean_tab_text, "auto_detection")
        print(f"[DEBUG] Tab switched from '{old_tab}' to '{self.current_tab}'")
        
        # Provide tablet-friendly feedback
        toast(f"Switched to {clean_tab_text} Analytics")
        
        # Only load tab content if we have a project selected
        if self.current_project_id:
            print(f"[DEBUG] Loading content for tab: {self.current_tab}")
            self.load_tab_content()
        else:
            print(f"[DEBUG] No project selected, skipping tab content load")
    
    def on_current_tab_change(self, instance_tabs, current_tab_instance):
        """Alternative handler for tab changes using current_tab property"""
        print(f"[DEBUG] on_current_tab_change called")
        print(f"[DEBUG] current_tab_instance: {current_tab_instance}")
        
        if hasattr(current_tab_instance, 'text'):
            tab_text = current_tab_instance.text
            print(f"[DEBUG] current_tab_instance.text: '{tab_text}'")
            # Use the same logic as on_tab_switch
            self.on_tab_switch(instance_tabs, current_tab_instance, None, tab_text)
        else:
            print(f"[DEBUG] current_tab_instance has no text attribute")
    
    def manual_switch_to_tab(self, tab_name: str):
        """Manually switch to a specific tab (fallback method)"""
        print(f"[DEBUG] manual_switch_to_tab called for: {tab_name}")
        
        if tab_name not in ["data_exploration", "auto_detection", "descriptive", "inferential", "qualitative"]:
            print(f"[DEBUG] Invalid tab name: {tab_name}")
            return
        
        old_tab = self.current_tab
        self.current_tab = tab_name
        print(f"[DEBUG] Manually switched from '{old_tab}' to '{self.current_tab}'")
        
        if self.current_project_id:
            print(f"[DEBUG] Loading content for manually switched tab: {self.current_tab}")
            self.load_tab_content()
        else:
            print(f"[DEBUG] No project selected for manual tab switch")
    
    def check_active_tab(self, dt):
        """Periodically check which tab is active and load content if needed"""
        if not self.current_project_id or not hasattr(self.ids, 'analytics_tabs'):
            return
        
        try:
            tabs = self.ids.analytics_tabs
            if hasattr(tabs, 'current_tab') and tabs.current_tab:
                current_tab_widget = tabs.current_tab
                
                # Try to get the tab text/title
                tab_text = None
                if hasattr(current_tab_widget, 'text'):
                    tab_text = current_tab_widget.text
                elif hasattr(current_tab_widget, 'title'):
                    tab_text = current_tab_widget.title
                
                if tab_text:
                    # Clean up the tab text using the same logic as on_tab_switch
                    clean_tab_text = tab_text
                    
                    # Remove KivyMD font formatting
                    if '[/font]' in clean_tab_text:
                        clean_tab_text = clean_tab_text.split('[/font]')[-1].strip()
                    
                    # Remove emoji prefixes (🤖, 📊, 🔬, 📝)
                    if ' ' in clean_tab_text:
                        parts = clean_tab_text.split(' ')
                        # Find the actual text part (not emoji)
                        for part in parts:
                            if part and not any(ord(char) > 127 for char in part):  # ASCII text only
                                clean_tab_text = part
                                break
                    
                    tab_map = {
                        "Explore": "data_exploration",
                        "Auto-Detection": "auto_detection",
                        "Descriptive": "descriptive", 
                        "Inferential": "inferential",
                        "Qualitative": "qualitative"
                    }
                    
                    detected_tab = tab_map.get(clean_tab_text, "auto_detection")
                    
                    # If detected tab is different from current tab, switch and load content
                    if detected_tab != self.current_tab:
                        print(f"[DEBUG] check_active_tab detected tab change: '{self.current_tab}' -> '{detected_tab}'")
                        old_tab = self.current_tab
                        self.current_tab = detected_tab
                        
                        # Load content for the newly detected tab
                        self.load_tab_content()
                        
                        # Unschedule this check after successful detection to avoid constant checking
                        Clock.unschedule(self.check_active_tab)
                        
                        # Reschedule for future tab changes
                        Clock.schedule_interval(self.check_active_tab, 2.0)
                        return
        
        except Exception as e:
            print(f"[DEBUG] Error in check_active_tab: {e}")

    def update_tablet_quick_stats(self):
        """Update quick statistics with tablet-optimized layout"""
        if not hasattr(self.ids, 'stats_container'):
            return
            
        try:
            stats_container = self.ids.stats_container
            stats_container.clear_widgets()
            
            if not self.current_project_id:
                return
                
            stats = self.get_project_stats()
            
            # Enhanced stat items for tablets with emojis and better descriptions
            # Updated with valid Material Design icon names
            stat_items = [
                ("Total Responses", f"{stats.get('total_responses', 0):,}", "database-outline", 
                 f"Survey responses collected", (0.2, 0.6, 1.0, 1)),
                (" Questions", f"{stats.get('total_questions', 0)}", "help-circle-outline", 
                 f"Questions in survey", (0.2, 0.8, 0.6, 1)),
                ("Completion Rate", f"{stats.get('completion_rate', 0):.1f}%", "chart-line", 
                 f"Response completion rate", (0.8, 0.6, 0.2, 1)),
                ("Participants", f"{stats.get('unique_respondents', 0):,}", "account-group-outline", 
                 f"Unique respondents", (0.6, 0.2, 0.8, 1)),
            ]
            
            # Create tablet-optimized stat cards
            for label, value, icon, note, color in stat_items:
                try:
                    card = self.create_tablet_stat_card(
                        title=label, 
                        value=str(value), 
                        icon=icon, 
                        note=note,
                        color=color
                    )
                    stats_container.add_widget(card)
                except Exception as card_error:
                    print(f"Error creating stat card for {label}: {card_error}")
                    
        except Exception as e:
            print(f"Error updating tablet quick stats: {e}")

    def create_tablet_stat_card(self, title, value, icon, note, color):
        """Create tablet-optimized statistics card"""
        card = MDCard(
            orientation="vertical",
            padding=self.TABLET_PADDING,
            spacing=dp(12),
            size_hint_y=None,
            height=dp(190),  # Reduced by 5% from dp(200) to dp(190)
            elevation=3,
            md_bg_color=(1, 1, 1, 1),
            radius=[12, 12, 12, 12]
        )
        
        # Header with icon and title
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(42),  # Reduced by 5% from dp(44) to dp(42)
            adaptive_height=True
        )
        
        # Fixed icon widget with proper sizing
        icon_widget = MDIconButton(
            icon=icon,
            theme_icon_color="Custom",
            icon_color=color,
            disabled=True,
            size_hint=(None, None),
            size=(dp(42), dp(42)),  # Reduced by 5% from dp(44) to dp(42)
            pos_hint={"center_y": 0.5}
        )
        
        title_label = MDLabel(
            text=title,
            font_style="Button",
            theme_text_color="Primary",
            bold=True,
            size_hint_x=1,
            adaptive_height=True,
            pos_hint={"center_y": 0.5}
        )
        
        header_layout.add_widget(icon_widget)
        header_layout.add_widget(title_label)
        
        # Value display
        value_label = MDLabel(
            text=value,
            font_style="H4",  # Large font for tablets
            theme_text_color="Primary",
            bold=True,
            halign="left",
            size_hint_y=None,
            height=dp(56)  # Increased from dp(48) to dp(56)
        )
        
        # Note
        note_label = MDLabel(
            text=note,
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(36)  # Increased from dp(32) to dp(36)
        )
        
        card.add_widget(header_layout)
        card.add_widget(value_label)
        card.add_widget(note_label)
        
        return card

    def get_project_stats(self):
        """Get enhanced project statistics for tablets"""
        if not self.current_project_id:
            return {}
            
        try:
            # Use analytics service for enhanced project stats
            stats = self.analytics_service.get_project_stats(self.current_project_id)
            
            if 'error' in stats:
                print(f"Error getting project stats: {stats['error']}")
                return {}
            
            # Calculate enhanced metrics for tablets
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

    def create_tablet_empty_state_card(self, title, message, icon, action_text=None, action_callback=None):
        """Create tablet-optimized empty state card"""
        card = MDCard(
            orientation="vertical",
            padding=self.TABLET_PADDING * 1.5,
            spacing=self.TABLET_SPACING,
            size_hint_y=None,
            height=dp(600),  # Increased from dp(500) to dp(600) for better proportion
            elevation=3,
            md_bg_color=(0.98, 0.99, 1.0, 1),
            radius=[16, 16, 16, 16]
        )
        
        # Center content
        center_layout = MDBoxLayout(
            orientation="vertical",
            spacing=self.TABLET_SPACING,
            size_hint_y=None,
            height=dp(480),  # Increased from dp(400) to dp(480) proportionally
            pos_hint={"center_x": 0.5}
        )
        
        # Icon with proper sizing
        icon_widget = MDIconButton(
            icon=icon,
            theme_icon_color="Custom",
            icon_color=(0.4, 0.6, 1.0, 1),
            disabled=True,
            size_hint=(None, None),
            size=(dp(96), dp(96)),  # Increased from dp(80) to dp(96) for better proportion
            pos_hint={"center_x": 0.5}
        )
        
        # Title
        title_label = MDLabel(
            text=title,
            font_style="H4",
            theme_text_color="Primary",
            halign="center",
            bold=True,
            size_hint_y=None,
            height=dp(56)  # Increased from dp(48) to dp(56)
        )
        
        # Message
        message_label = MDLabel(
            text=message,
            font_style="Body1",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(180),  # Increased from dp(150) to dp(180) for more content space
            text_size=(None, None)
        )
        
        center_layout.add_widget(icon_widget)
        center_layout.add_widget(title_label)
        center_layout.add_widget(message_label)
        
        if action_text and action_callback:
            action_button = MDRaisedButton(
                text=action_text,
                size_hint=(None, None),
                height=self.TABLET_BUTTON_HEIGHT,
                width=dp(200),
                font_size=self.TABLET_FONT_SIZE,
                md_bg_color=(0.4, 0.6, 1.0, 1),
                on_release=lambda x: action_callback()
            )
            center_layout.add_widget(action_button)
        
        card.add_widget(center_layout)
        return card

    def create_backend_error_widget(self):
        """Create tablet-optimized backend error widget"""
        error_card = MDCard(
            orientation="vertical",
            padding=self.TABLET_PADDING,
            spacing=self.TABLET_SPACING,
            size_hint_y=None,
            height=dp(320),
            elevation=3,
            md_bg_color=(1, 0.95, 0.95, 1),
            radius=[16, 16, 16, 16]
        )
        
        # Error header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(56)
        )
        
        # Fixed error icon sizing
        error_icon = MDIconButton(
            icon="alert-circle-outline",  # Updated to use outline version
            theme_icon_color="Custom",
            icon_color=(0.8, 0.2, 0.2, 1),
            disabled=True,
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            pos_hint={"center_y": 0.5}
        )
        
        error_title = MDLabel(
            text="Analytics Backend Unavailable",
            font_style="H5",
            theme_text_color="Custom",
            text_color=(0.8, 0.2, 0.2, 1),
            bold=True,
            pos_hint={"center_y": 0.5}
        )
        
        header_layout.add_widget(error_icon)
        header_layout.add_widget(error_title)
        error_card.add_widget(header_layout)
        
        # Error message optimized for tablets
        error_message = MDLabel(
            text="The analytics backend is not responding. To fix this:\n\n" +
                 " 1. Start the FastAPI server on port 8001\n" +
                 " 2. Run: python backend/fastapi/start_analytics_backend.py\n" +
                 " 3. Check backend logs for any errors\n" +
                 " 4. Click 'Retry Connection' when ready",
            font_style="Body1",
            theme_text_color="Custom",
            text_color=(0.6, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(160)
        )
        error_card.add_widget(error_message)
        
        # Action buttons
        button_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=self.TABLET_BUTTON_HEIGHT + dp(8)
        )
        
        retry_button = MDRaisedButton(
            text=" Retry Connection",
            size_hint_x=1,
            height=self.TABLET_BUTTON_HEIGHT,
            font_size=self.TABLET_FONT_SIZE,
            md_bg_color=(0.8, 0.4, 0.2, 1),
            on_release=lambda x: self.load_tab_content()
        )
        
        help_button = MDFlatButton(
            text=" Get Help",
            size_hint_x=0.6,
            height=self.TABLET_BUTTON_HEIGHT,
            font_size=self.TABLET_FONT_SIZE,
            on_release=lambda x: self.show_backend_help()
        )
        
        button_layout.add_widget(retry_button)
        button_layout.add_widget(help_button)
        error_card.add_widget(button_layout)
        
        return error_card

    # Enhanced analysis methods for tablets
    def load_data_exploration(self):
        """Load data exploration with tablet feedback"""
        print(f"[DEBUG] load_data_exploration called")
        print(f"[DEBUG] current_project_id: {self.current_project_id}")
        print(f"[DEBUG] has data_exploration_handler: {hasattr(self, 'data_exploration_handler')}")
        
        if not self.current_project_id:
            print(f"[DEBUG] No project selected, showing message")
            self.show_select_project_message()
            return
        
        if hasattr(self, 'data_exploration_handler'):
            print(f"[DEBUG] Calling data_exploration_handler.explore_project_data")
            toast(" Loading data exploration...")
            self.data_exploration_handler.explore_project_data(self.current_project_id)
        else:
            print(f"[DEBUG] ERROR: Data exploration handler not available")
            toast(" Data exploration handler not available")

    def load_auto_detection(self):
        """Load auto-detection with tablet feedback"""
        print(f"[DEBUG] load_auto_detection called")
        print(f"[DEBUG] current_project_id: {self.current_project_id}")
        print(f"[DEBUG] has auto_detection_handler: {hasattr(self, 'auto_detection_handler')}")
        
        if not self.current_project_id:
            print(f"[DEBUG] No project ID, showing welcome state")
            self.show_tablet_welcome_state()
            return
        
        if hasattr(self, 'auto_detection_handler'):
            print(f"[DEBUG] Calling auto_detection_handler.run_auto_detection")
            toast(" Running intelligent data analysis...")
            self.auto_detection_handler.run_auto_detection(self.current_project_id)
        else:
            print(f"[DEBUG] ERROR: Auto-detection handler not available")
            toast(" Auto-detection handler not available")

    def load_descriptive(self):
        """Load descriptive analytics with tablet feedback"""
        print(f"[DEBUG] load_descriptive called")
        print(f"[DEBUG] current_project_id: {self.current_project_id}")
        print(f"[DEBUG] has descriptive_handler: {hasattr(self, 'descriptive_handler')}")
        
        if not self.current_project_id:
            print(f"[DEBUG] No project selected, showing message")
            self.show_select_project_message()
            return
        
        if hasattr(self, 'descriptive_handler'):
            print(f"[DEBUG] Calling descriptive_handler.run_descriptive_analysis")
            toast(" Loading descriptive analytics selection...")
            self.descriptive_handler.run_descriptive_analysis(self.current_project_id)
        else:
            print(f"[DEBUG] ERROR: Descriptive analytics handler not available")
            toast(" Descriptive analytics handler not available")
    
    def debug_load_descriptive(self):
        """Debug method to manually trigger descriptive analytics"""
        print(f"[DEBUG] debug_load_descriptive called manually")
        self.current_tab = "descriptive"
        self.load_descriptive()

    def load_qualitative(self):
        """Load qualitative analytics with tablet feedback"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
        
        if hasattr(self, 'qualitative_handler'):
            toast(" Analyzing text and qualitative data...")
            self.qualitative_handler.run_text_analysis(self.current_project_id)
        else:
            toast("❌ Qualitative analytics handler not available")

    def load_inferential(self):
        """Load inferential statistics with tablet placeholder"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
        
        # Use the helper method to get the content area
        content = self.get_tab_content('inferential')
        
        if not content:
            print(f"[DEBUG] ERROR: Could not get inferential content area")
            return
            
        content.clear_widgets()
        
        # Create fixed-height coming soon interface
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDRaisedButton, MDIconButton
        
        coming_soon_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(350),  # Fixed height
            padding=dp(24),
            spacing=dp(20),
            md_bg_color=(0.99, 0.98, 1.0, 1),
            elevation=3,
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(56)
        )
        
        # Fixed icon sizing for inferential statistics
        inferential_icon = MDIconButton(
            icon="flask-outline",  # Updated to use outline version
            theme_icon_color="Custom",
            icon_color=(0.4, 0.2, 0.8, 1),
            disabled=True,
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            pos_hint={"center_y": 0.5}
        )
        
        header_label = MDLabel(
            text="🔬 Inferential Statistics",
            font_style="H4",
            theme_text_color="Primary",
            bold=True,
            pos_hint={"center_y": 0.5}
        )
        
        header_layout.add_widget(inferential_icon)
        header_layout.add_widget(header_label)
        coming_soon_card.add_widget(header_layout)
        
        # Coming soon message
        message_text = """ Advanced Statistical Inference - Coming Soon!

This powerful module will include:

 Hypothesis Testing
   • t-tests, chi-square tests, ANOVA
   • Statistical significance testing
 Regression Analysis  
   • Linear and logistic regression
   • Multiple regression models

 Advanced Methods
   • Confidence intervals and p-values
   • Effect size calculations
   • Power analysis

 Stay tuned for these advanced analytics capabilities!"""
        
        message_label = MDLabel(
            text=message_text,
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(220)
        )
        coming_soon_card.add_widget(message_label)
        
        # Action button
        action_button = MDRaisedButton(
            text=" Request Early Access",
            size_hint=(None, None),
            height=dp(48),
            width=dp(200),
            font_size="16sp",
            md_bg_color=(0.4, 0.2, 0.8, 1),
            on_release=lambda x: toast(" Early access request noted! We'll notify you when available.")
        )
        coming_soon_card.add_widget(action_button)
        
        content.add_widget(coming_soon_card)
        print(f"[DEBUG] Inferential statistics placeholder created successfully!")

    # Tablet-specific utility methods
    def show_select_project_message(self):
        """Show tablet-optimized project selection message"""
        toast(" Please select a project from the dropdown above")

    def show_project_selection_guide(self):
        """Show tablet-optimized project selection guide"""
        toast(" Tap the project dropdown above to select a project for analysis")

    def show_backend_help(self):
        """Show backend setup help for tablets"""
        toast(" Check the documentation for backend setup instructions")

    def navigate_to_projects(self):
        """Navigate to projects screen (placeholder)"""
        toast(" Navigate to Projects tab to create your first project")

    def set_loading(self, loading):
        """Set loading state with tablet feedback"""
        self.is_loading = loading
        if hasattr(self.ids, 'loading_spinner'):
            self.ids.loading_spinner.active = loading
        
        if loading:
            toast(" Processing...")

    def show_error(self, message):
        """Show error message with tablet formatting"""
        toast(f"❌ Error: {message}")

    def refresh_analysis(self):
        """Refresh current analysis with tablet feedback"""
        if self.current_project_id:
            toast(" Refreshing analysis...")
            self.load_tab_content()
        else:
            toast(" Select a project first to refresh analysis")

    def create_empty_state_widget(self, message):
        """Create simple empty state widget for backward compatibility"""
        return MDLabel(
            text=message,
            halign="center",
            theme_text_color="Secondary",
            font_style="Body1"
        )

    def on_window_resize(self, window, width, height):
        """Handle window resize for tablets"""
        self.update_responsive_layout()
        
        # Update tablet detection
        self.is_tablet = self._detect_tablet()

    def update_responsive_layout(self):
        """Update responsive layout optimized for tablets"""
        try:
            window_width = Window.width
            window_height = Window.height
            
            # Determine optimal layout for tablets
            if window_width < 800:  # Portrait tablet or small tablet
                stats_cols = 2
                card_spacing = dp(16)
            elif window_width < 1200:  # Landscape tablet
                stats_cols = 4
                card_spacing = self.TABLET_SPACING
            else:  # Large tablet
                stats_cols = 4
                card_spacing = self.TABLET_SPACING
                
            # Update stats container
            if hasattr(self.ids, 'stats_container'):
                container = self.ids.stats_container
                container.cols = stats_cols
                container.spacing = card_spacing
                
            # Update main content padding based on orientation
            if hasattr(self.ids, 'main_content'):
                if window_width > window_height:  # Landscape
                    self.ids.main_content.padding = [self.TABLET_PADDING * 1.5, self.TABLET_PADDING, self.TABLET_PADDING * 1.5, self.TABLET_PADDING]
                else:  # Portrait
                    self.ids.main_content.padding = [self.TABLET_PADDING, self.TABLET_PADDING * 1.5, self.TABLET_PADDING, self.TABLET_PADDING]
                
        except Exception as e:
            print(f"Error in responsive layout: {e}")
            # Fallback to safe values
            if hasattr(self.ids, 'stats_container'):
                self.ids.stats_container.cols = 2

    def load_tab_content(self):
        """Load content for current tab with tablet optimizations"""
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
        """Load project data characteristics for tablets"""
        # This is now handled by specialized handlers
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
            print(f"[DEBUG] Screen-level IDs available: {list(self.ids.keys())}")
            
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
            
            # First try: check if the content is directly accessible through screen IDs
            if hasattr(self.ids, content_id):
                content = getattr(self.ids, content_id)
                print(f"[DEBUG] Found {content_id} directly in screen ids!")
                return content
            
            # Second try: check if tabs widget has the content in its IDs
            if hasattr(tabs, 'ids') and content_id in tabs.ids:
                content = tabs.ids[content_id]
                print(f"[DEBUG] Found {content_id} in tabs.ids!")
                return content
            
            # Third try: KivyMD tabs structure search
            if hasattr(tabs, 'carousel') and hasattr(tabs.carousel, 'slides'):
                slides = tabs.carousel.slides
                print(f"[DEBUG] Found {len(slides)} tab content slides")
                
                for i, slide in enumerate(slides):
                    print(f"[DEBUG] Searching slide {i}: {type(slide).__name__}")
                    # Check if the slide has the content in its IDs
                    if hasattr(slide, 'ids') and content_id in slide.ids:
                        content = slide.ids[content_id]
                        print(f"[DEBUG] Found {content_id} in slide {i} ids!")
                        return content
                    
                    # Search through the slide's widget tree
                    content = self._find_widget_by_id(slide, content_id)
                    if content:
                        print(f"[DEBUG] Found {content_id} in slide {i} widget tree, type: {type(content)}")
                        return content
                    else:
                        print(f"[DEBUG] Could not find {content_id} in slide {i}")
            else:
                print(f"[DEBUG] No carousel/slides found in tabs")
                # Fallback: search through all children of the tabs widget
                content = self._find_widget_by_id(tabs, content_id)
                if content:
                    print(f"[DEBUG] Found {content_id} in tabs fallback search")
                    return content
            
            print(f"[DEBUG] Could not find {content_id} in any location")
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
            
            # Try multiple ways to get the widget ID
            widget_id = None
            if hasattr(widget, 'id'):
                widget_id = widget.id
            elif hasattr(widget, '_id'):
                widget_id = widget._id
            
            print(f"[DEBUG] {indent}Checking widget: {widget_type} (id: {widget_id})")
            
            # Print available IDs if any - do this first to see what's available
            if hasattr(widget, 'ids') and widget.ids:
                print(f"[DEBUG] {indent}Available IDs: {list(widget.ids.keys())}")
            
            # Check if this widget has the ID we're looking for
            if hasattr(widget, 'ids') and target_id in widget.ids:
                print(f"[DEBUG] {indent}Found {target_id} in widget's ids!")
                return widget.ids[target_id]
            
            # Check if this widget itself has the target ID
            if widget_id == target_id:
                print(f"[DEBUG] {indent}Widget itself has target ID!")
                return widget
            
            # Recursively search children (but limit depth to avoid infinite recursion)
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