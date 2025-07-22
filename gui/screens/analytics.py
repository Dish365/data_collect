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

import threading
from datetime import datetime

Builder.load_file('kv/analytics.kv')

class AnalyticsTab(MDBoxLayout, MDTabsBase):
    """Base class for analytics tab content - Tablet Optimized"""
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
    TABLET_CARD_HEIGHT = dp(300)
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
            self.ids.top_bar.set_title("📊 Analytics Dashboard")
        
        self.setup_analytics_service()
        self.load_projects()
        self.setup_tablet_optimized_tabs()
        self.update_responsive_layout()
        self.update_tablet_quick_stats()
        
        # Show welcome message for tablets
        if self.is_tablet and not self.current_project_id:
            self.show_tablet_welcome_state()

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
        from services.auto_detection_analytics import AutoDetectionAnalyticsHandler
        from services.descriptive_analytics import DescriptiveAnalyticsHandler
        from services.qualitative_analytics import QualitativeAnalyticsHandler
        
        # Initialize handlers with tablet awareness
        self.auto_detection_handler = AutoDetectionAnalyticsHandler(
            self.analytics_service, self
        )
        self.descriptive_handler = DescriptiveAnalyticsHandler(
            self.analytics_service, self
        )
        self.qualitative_handler = QualitativeAnalyticsHandler(
            self.analytics_service, self
        )

    def load_projects(self):
        """Load available projects with tablet-optimized presentation"""
        try:
            app = App.get_running_app()
            conn = app.db_service.get_db_connection()
            
            if conn is None:
                toast("📱 Database not initialized")
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
                self.ids.project_selector.text = "📊 Select Project for Analysis"
                self.ids.project_selector.font_size = self.TABLET_FONT_SIZE
                
        except Exception as e:
            print(f"Error loading projects: {e}")
            toast("❌ Error loading projects")
        finally:
            if conn:
                conn.close()

    def show_tablet_no_projects_state(self):
        """Show tablet-optimized message when no projects are available"""
        if hasattr(self.ids, 'auto_detection_content'):
            content = self.ids.auto_detection_content
            content.clear_widgets()
            
            no_projects_card = self.create_tablet_empty_state_card(
                title="🚀 Welcome to Analytics!",
                message="To get started with data analysis:\n\n" +
                        "1. 📝 Create a new project in the Projects tab\n" +
                        "2. 📊 Add some survey questions\n" +
                        "3. 📋 Collect responses from participants\n" +
                        "4. 🔬 Return here for powerful analytics insights!",
                icon="chart-line",
                action_text="Go to Projects",
                action_callback=lambda: self.navigate_to_projects()
            )
            content.add_widget(no_projects_card)

    def show_tablet_welcome_state(self):
        """Show tablet-optimized welcome state"""
        if hasattr(self.ids, 'auto_detection_content'):
            content = self.ids.auto_detection_content
            content.clear_widgets()
            
            welcome_card = self.create_tablet_empty_state_card(
                title="📊 Analytics Dashboard",
                message="Welcome to your data analytics workspace!\n\n" +
                        f"You have {len(self.project_list)} project(s) available.\n" +
                        "Select a project above to begin analyzing your data.",
                icon="lightbulb",
                action_text="Show Project Guide",
                action_callback=lambda: self.show_project_selection_guide()
            )
            content.add_widget(welcome_card)

    def open_project_menu(self):
        """Open tablet-optimized project selection dropdown menu"""
        if self.project_menu:
            self.project_menu.dismiss()
            
        if not self.project_list:
            toast("📋 No projects available")
            return
            
        menu_items = []
        for project in self.project_list:
            # Enhanced menu item text for tablets
            item_text = f"📊 {project['name']}\n" + \
                       f"📋 {project['response_count']} responses • " + \
                       f"👥 {project['respondent_count']} respondents"
            
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
            selector_text = f"📊 {project['name']}"
            if project['response_count'] > 0:
                selector_text += f" ({project['response_count']} responses)"
            self.ids.project_selector.text = selector_text
        
        # Update stats and characteristics
        self.update_tablet_quick_stats()
        self.load_project_data_characteristics()
        
        # Auto-run analysis with tablet feedback
        if self.current_tab == "auto_detection" or not hasattr(self, '_auto_analysis_run'):
            toast(f"🔬 Analyzing {project['name']}...")
            Clock.schedule_once(lambda dt: self.load_auto_detection(), 0.5)
            self._auto_analysis_run = True
        
        toast(f"✅ Selected: {project['name']}")

    def setup_tablet_optimized_tabs(self):
        """Setup analytics tabs optimized for tablets"""
        if not hasattr(self.ids, 'analytics_tabs'):
            return
            
        tabs = self.ids.analytics_tabs
        tabs.bind(on_tab_switch=self.on_tab_switch)
        
        # Enhance tab appearance for tablets
        for tab in tabs.get_tab_list():
            if hasattr(tab, 'title'):
                # Add emoji prefixes to tab titles for better visual hierarchy
                title_map = {
                    "Auto-Detection": "🤖 Auto-Detection",
                    "Descriptive": "📊 Descriptive", 
                    "Inferential": "🔬 Inferential",
                    "Qualitative": "📝 Qualitative"
                }
                if tab.title in title_map:
                    tab.title = title_map[tab.title]

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        """Handle tab switching with tablet optimizations"""
        # Remove emoji prefixes for internal logic
        clean_tab_text = tab_text.split(' ', 1)[-1] if ' ' in tab_text else tab_text
        
        tab_map = {
            "Auto-Detection": "auto_detection",
            "Descriptive": "descriptive", 
            "Inferential": "inferential",
            "Qualitative": "qualitative"
        }
        
        self.current_tab = tab_map.get(clean_tab_text, "auto_detection")
        
        # Provide tablet-friendly feedback
        toast(f"📋 Switched to {clean_tab_text} Analytics")
        
        self.load_tab_content()

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
            stat_items = [
                ("📊 Total Responses", f"{stats.get('total_responses', 0):,}", "database", 
                 f"Survey responses collected", (0.2, 0.6, 1.0, 1)),
                ("❓ Questions", f"{stats.get('total_questions', 0)}", "help-circle", 
                 f"Questions in survey", (0.2, 0.8, 0.6, 1)),
                ("📈 Completion Rate", f"{stats.get('completion_rate', 0):.1f}%", "chart-line", 
                 f"Response completion rate", (0.8, 0.6, 0.2, 1)),
                ("👥 Participants", f"{stats.get('unique_respondents', 0):,}", "account-group", 
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
            height=dp(140),  # Taller for tablets
            elevation=3,
            md_bg_color=(1, 1, 1, 1),
            radius=[12, 12, 12, 12]
        )
        
        # Header with icon and title
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(40)
        )
        
        icon_widget = MDIconButton(
            icon=icon,
            theme_icon_color="Custom",
            icon_color=color,
            disabled=True,
            size_hint_x=None,
            width=self.TABLET_ICON_SIZE + dp(8)
        )
        
        title_label = MDLabel(
            text=title,
            font_style="Button",
            theme_text_color="Primary",
            bold=True,
            size_hint_x=1
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
            height=dp(48)
        )
        
        # Note
        note_label = MDLabel(
            text=note,
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(32)
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
            height=dp(400),
            elevation=3,
            md_bg_color=(0.98, 0.99, 1.0, 1),
            radius=[16, 16, 16, 16]
        )
        
        # Center content
        center_layout = MDBoxLayout(
            orientation="vertical",
            spacing=self.TABLET_SPACING,
            size_hint_y=None,
            height=dp(320)
        )
        
        # Icon
        icon_widget = MDIconButton(
            icon=icon,
            theme_icon_color="Custom",
            icon_color=(0.4, 0.6, 1.0, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(64),
            user_font_size="48sp"
        )
        
        # Title
        title_label = MDLabel(
            text=title,
            font_style="H4",
            theme_text_color="Primary",
            halign="center",
            bold=True,
            size_hint_y=None,
            height=dp(48)
        )
        
        # Message
        message_label = MDLabel(
            text=message,
            font_style="Body1",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(120)
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
        
        error_icon = MDIconButton(
            icon="alert-circle",
            theme_icon_color="Custom",
            icon_color=(0.8, 0.2, 0.2, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(48)
        )
        
        error_title = MDLabel(
            text="🚨 Analytics Backend Unavailable",
            font_style="H5",
            theme_text_color="Custom",
            text_color=(0.8, 0.2, 0.2, 1),
            bold=True
        )
        
        header_layout.add_widget(error_icon)
        header_layout.add_widget(error_title)
        error_card.add_widget(header_layout)
        
        # Error message optimized for tablets
        error_message = MDLabel(
            text="The analytics backend is not responding. To fix this:\n\n" +
                 "🔧 1. Start the FastAPI server on port 8001\n" +
                 "🚀 2. Run: python backend/fastapi/start_analytics_backend.py\n" +
                 "📋 3. Check backend logs for any errors\n" +
                 "🔄 4. Click 'Retry Connection' when ready",
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
            text="🔄 Retry Connection",
            size_hint_x=1,
            height=self.TABLET_BUTTON_HEIGHT,
            font_size=self.TABLET_FONT_SIZE,
            md_bg_color=(0.8, 0.4, 0.2, 1),
            on_release=lambda x: self.load_tab_content()
        )
        
        help_button = MDFlatButton(
            text="❓ Get Help",
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
    def load_auto_detection(self):
        """Load auto-detection with tablet feedback"""
        if not self.current_project_id:
            self.show_tablet_welcome_state()
            return
        
        if hasattr(self, 'auto_detection_handler'):
            toast("🤖 Running intelligent data analysis...")
            self.auto_detection_handler.run_auto_detection(self.current_project_id)
        else:
            toast("❌ Auto-detection handler not available")

    def load_descriptive(self):
        """Load descriptive analytics with tablet feedback"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
        
        if hasattr(self, 'descriptive_handler'):
            toast("📊 Loading descriptive analytics...")
            self.descriptive_handler.run_descriptive_analysis(self.current_project_id)
        else:
            toast("❌ Descriptive analytics handler not available")

    def load_qualitative(self):
        """Load qualitative analytics with tablet feedback"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
        
        if hasattr(self, 'qualitative_handler'):
            toast("📝 Analyzing text and qualitative data...")
            self.qualitative_handler.run_text_analysis(self.current_project_id)
        else:
            toast("❌ Qualitative analytics handler not available")

    def load_inferential(self):
        """Load inferential statistics with tablet placeholder"""
        if not self.current_project_id:
            self.show_select_project_message()
            return
        
        # Show tablet-optimized coming soon message
        if hasattr(self.ids, 'inferential_content'):
            content = self.ids.inferential_content
            content.clear_widgets()
            
            coming_soon_card = self.create_tablet_empty_state_card(
                title="🔬 Inferential Statistics",
                message="Advanced statistical inference features are coming soon!\n\n" +
                        "This will include:\n" +
                        "• Hypothesis testing\n" +
                        "• Regression analysis\n" +
                        "• ANOVA and statistical significance tests\n" +
                        "• Confidence intervals and p-values",
                icon="microscope",
                action_text="📧 Request Early Access",
                action_callback=lambda: toast("🚀 Early access request noted!")
            )
            content.add_widget(coming_soon_card)

    # Tablet-specific utility methods
    def show_select_project_message(self):
        """Show tablet-optimized project selection message"""
        toast("📊 Please select a project from the dropdown above")

    def show_project_selection_guide(self):
        """Show tablet-optimized project selection guide"""
        toast("💡 Tap the project dropdown above to select a project for analysis")

    def show_backend_help(self):
        """Show backend setup help for tablets"""
        toast("💡 Check the documentation for backend setup instructions")

    def navigate_to_projects(self):
        """Navigate to projects screen (placeholder)"""
        toast("🚀 Navigate to Projects tab to create your first project")

    def set_loading(self, loading):
        """Set loading state with tablet feedback"""
        self.is_loading = loading
        if hasattr(self.ids, 'loading_spinner'):
            self.ids.loading_spinner.active = loading
        
        if loading:
            toast("⏳ Processing...")

    def show_error(self, message):
        """Show error message with tablet formatting"""
        toast(f"❌ Error: {message}")

    def refresh_analysis(self):
        """Refresh current analysis with tablet feedback"""
        if self.current_project_id:
            toast("🔄 Refreshing analysis...")
            self.load_tab_content()
        else:
            toast("📊 Select a project first to refresh analysis")

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

    def load_project_data_characteristics(self):
        """Load project data characteristics for tablets"""
        # This is now handled by specialized handlers
        pass