import os
os.environ['KIVY_LOG_MODE'] = 'PYTHON'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.app import MDApp
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.lang import Builder

# Workaround for KivyMD 2.0.1 app reference issues
class SafeScreenManager:
    """Safe screen manager that doesn't crash when screens don't exist"""
    def __init__(self):
        self._real_screen_manager = None
    
    def set_real_manager(self, manager):
        self._real_screen_manager = manager
    
    def get_screen(self, name):
        if self._real_screen_manager and hasattr(self._real_screen_manager, 'get_screen'):
            try:
                return self._real_screen_manager.get_screen(name)
            except:
                # Return a dummy object with common screen attributes
                class DummyScreen:
                    current_project_id = None
                    def __getattr__(self, attr):
                        def dummy_method(*args, **kwargs):
                            pass
                        return dummy_method
                return DummyScreen()
        else:
            class DummyScreen:
                current_project_id = None
                def __getattr__(self, attr):
                    def dummy_method(*args, **kwargs):
                        pass
                    return dummy_method
            return DummyScreen()
    
    def __getattr__(self, attr):
        if self._real_screen_manager:
            return getattr(self._real_screen_manager, attr)
        else:
            def dummy_method(*args, **kwargs):
                pass
            return dummy_method

def setup_app_theme_workaround():
    """Set up workaround for KivyMD app reference issues"""
    # Make sure App class has theme_cls attribute for KV files
    if not hasattr(App, 'theme_cls'):
        App.theme_cls = None
    
    # Set up safe screen manager
    if not hasattr(App, 'root'):
        App.root = SafeScreenManager()

# Call workaround immediately
setup_app_theme_workaround()

# Import screens
from screens.login import LoginScreen
from screens.dashboard import DashboardScreen
from screens.projects import ProjectsScreen
from screens.project_creation import ProjectCreationScreen
from screens.data_collection import DataCollectionScreen
from screens.analytics import AnalyticsScreen
from screens.form_builder_modern import FormBuilderScreen
from screens.sync import SyncScreen
from screens.signup import SignUpScreen

from screens.data_exploration import DataExplorationScreen
from screens.qualitative_analytics import QualitativeAnalyticsScreen
from screens.auto_detection import AutoDetectionScreen
from screens.descriptive_analytics import DescriptiveAnalyticsScreen
from screens.inferential_analytics import InferentialAnalyticsScreen

from kivy.modules import inspector

# Import services
from services.database import DatabaseService
from services.sync_service import SyncService
from services.auth_service import AuthService
from services.form_service_modern import ModernFormService as FormService

class ResearchCollectorApp(MDApp):
    user_display_name = StringProperty("Guest")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize theme immediately to prevent KV loading issues
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_palette = "Blue"    
        self.theme_cls.primary_hue = "500"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.dynamic_color = True
        
        # Set App class attributes to this instance for KV files
        App.theme_cls = self.theme_cls
        App.user_display_name = self.user_display_name
    
    def build(self):
        # Responsive window sizing for tablet optimization
        if platform != 'android':
            # Detect screen size and set appropriate window dimensions
            self.setup_responsive_window()
        
        # Bind to window size changes for orientation handling
        Window.bind(on_resize=self.on_window_resize)
        
        # Initialize services
        self.db_service = DatabaseService()
        self.sync_service = SyncService(self.db_service)
        self.auth_service = AuthService()
        self.form_service = FormService(self.auth_service, self.db_service, self.sync_service)
        from services.data_collection_service import DataCollectionService
        self.data_collection_service = DataCollectionService(self.auth_service, self.db_service, self.sync_service)
        from services.dashboard_service import DashboardService
        self.dashboard_service = DashboardService(self.auth_service, self.db_service)
        from services.analytics_service import AnalyticsService
        self.analytics_service = AnalyticsService(self.auth_service, self.db_service)
        
        # Create screen manager (screens will be added in on_start)
        sm = ScreenManager()
        
        # Set root for KV files - use our safe wrapper
        App.root.set_real_manager(sm)
        
        inspector.create_inspector(Window, sm)
        
        return sm
    
    def load_kv_files(self):
        """Load all KV files now that theme is ready"""
        from kivy.lang import Builder
        import os
        
        kv_files = [
            # Screen KV files
            "kv/login.kv",
            "kv/dashboard.kv", 
            "kv/projects.kv",
            "kv/project_creation.kv",
            "kv/collect_data.kv",
            "kv/analytics.kv",
            "kv/form_builder_modern.kv",
            "kv/sync.kv",
            "kv/signup.kv",
            "kv/responses.kv",
            "kv/data_exploration.kv",
            "kv/qualitative_analytics.kv",
            "kv/auto_detection.kv",
            "kv/descriptive_analytics.kv",
            "kv/inferential_analytics.kv",
            # Widget KV files
            "kv/topbar.kv",
            "kv/team_member_dialog.kv",
            "kv/sync_item.kv",
            "kv/stat_card.kv",
            "kv/project_item.kv",
            "kv/project_dialog.kv",
            "kv/form_field_modern.kv",
            "kv/forgot_password_popup.kv",
            "kv/chart_widget.kv",
            "kv/activity_item.kv",
            "kv/loading_overlay.kv"
        ]
        
        for kv_file in kv_files:
            if os.path.exists(kv_file):
                try:
                    Builder.load_file(kv_file)
                    print(f"Loaded KV file: {kv_file}")
                except Exception as e:
                    print(f"Error loading KV file {kv_file}: {e}")
    
    def setup_responsive_window(self):
        """Setup responsive window sizing for tablet optimization"""
        # Set minimum window constraints
        Window.minimum_width = 800
        Window.minimum_height = 600
        
        # Set default tablet-friendly size if not on mobile
        Window.size = (1024, 768)
        
        print(f"Window initialized: {Window.size[0]}x{Window.size[1]}")
    
    def on_window_resize(self, window, width, height):
        """Handle window resize events for responsive layout"""
        print(f"Window resized to: {width}x{height}")
        
        # Update screen manager screens that support responsive layouts
        if hasattr(self.root, 'screen_manager'):
            sm = self.root.screen_manager
            current_screen = sm.current_screen
            
            # Update responsive screens
            responsive_screens = ['dashboard', 'analytics', 'form_builder', 'data_collection']
            
            if current_screen and hasattr(current_screen, 'name') and current_screen.name in responsive_screens:
                if hasattr(current_screen, 'on_window_resize'):
                    try:
                        current_screen.on_window_resize(width, height)
                    except Exception as e:
                        print(f"Error updating {current_screen.name} screen layout: {e}")
        
        # Update window properties
        self.update_window_properties(width, height)
    
    def update_window_properties(self, width, height):
        """Update window properties based on screen size"""
        # Prevent recursive resize loops by checking for reasonable bounds
        max_width = 3840  # 4K width limit
        max_height = 2160  # 4K height limit
        min_width = 800   # Minimum usable width
        min_height = 600  # Minimum usable height
        
        # Clamp dimensions to reasonable bounds
        width = max(min_width, min(width, max_width))
        height = max(min_height, min(height, max_height))
        
        # Determine if we're in landscape or portrait
        is_landscape = width > height
        
        # Only update window size if it's significantly different to prevent loops
        current_width = Window.width
        current_height = Window.height
        
        # Check if resize is needed (with tolerance to prevent micro-adjustments)
        resize_threshold = 50  # pixels
        width_diff = abs(current_width - width)
        height_diff = abs(current_height - height)
        
        if width_diff > resize_threshold or height_diff > resize_threshold:
            # Update window size only if needed
            Window.size = (width, height)
            print(f"Window resized to {width}x{height} ({'landscape' if is_landscape else 'portrait'})")
        
        # Update responsive elements without triggering more resizes
        self.update_global_responsive_elements(width, height)

    def update_global_responsive_elements(self, width, height):
        """Update global responsive elements based on screen size"""
        # You can add global responsive logic here
        # For example, updating theme spacing or global font sizes
        
        is_landscape = width > height
        
        # Update any global responsive elements based on screen size
        # This is where you'd add global theme updates, font scaling, etc.
        pass
    
    def on_start(self):
        """Called when app starts"""
        # Use Clock to delay initialization to ensure app is fully running
        from kivy.clock import Clock
        Clock.schedule_once(self._delayed_init, 0.1)
    
    def _delayed_init(self, dt):
        """Delayed initialization after app is fully running"""
        # Load KV files now that theme and app are fully initialized
        self.load_kv_files()
        
        # Add screens after KV files are loaded
        self.add_screens()
        
        # Initialize database
        self.db_service.init_database()
        
        # Migrate existing data to include user_id fields
        self.db_service.migrate_existing_data()
        
        # Check if user is already authenticated
        if self.auth_service.is_authenticated():
            self.handle_successful_login()
        else:
            # User needs to login
            self.root.current = "login"
    
    def add_screens(self):
        """Add all screens to the screen manager"""
        # Add screens
        self.root.add_widget(LoginScreen(name='login'))
        self.root.add_widget(SignUpScreen(name='signup'))
        self.root.add_widget(DashboardScreen(name='dashboard'))
        self.root.add_widget(ProjectsScreen(name='projects'))
        self.root.add_widget(ProjectCreationScreen(name='project_creation'))
        self.root.add_widget(DataCollectionScreen(name='data_collection'))
        self.root.add_widget(AnalyticsScreen(name='analytics'))
        self.root.add_widget(FormBuilderScreen(name='form_builder'))
        self.root.add_widget(SyncScreen(name='sync'))

        self.root.add_widget(DataExplorationScreen(name='data_exploration'))
        self.root.add_widget(AutoDetectionScreen(name='auto_detection'))
        self.root.add_widget(DescriptiveAnalyticsScreen(name='descriptive_analytics'))
        self.root.add_widget(InferentialAnalyticsScreen(name='inferential_analytics'))
        self.root.add_widget(QualitativeAnalyticsScreen(name='qualitative_analytics'))
        
    def handle_successful_login(self):
        """Handle successful login - set up user context and navigate to dashboard"""
        try:
            self.update_user_display_name()
            
            # Get user data and set database context
            user_data = self.auth_service.get_user_data()
            if user_data and 'id' in user_data:
                user_id = user_data['id']
                
                # Set database user context
                self.db_service.set_current_user(user_id)
                
                # Clean up stale sync data to prevent incorrect counts
                self.db_service.cleanup_stale_sync_data()
                
                # Verify user data integrity
                self.db_service.ensure_user_data_integrity(user_id)
                
                # Verify database context was set correctly
                db_user = self.db_service.get_current_user()
                if db_user != user_id:
                    # Try setting it again
                    self.db_service.set_current_user(user_id)
                    db_user = self.db_service.get_current_user()
                    if db_user != user_id:
                        print(f"Error: Failed to establish database context for user {user_id}")
                
                # Reset dashboard for new user
                dashboard_screen = self.get_dashboard_screen()
                if dashboard_screen:
                    dashboard_screen.reset_for_new_user()
                
                # Navigate to dashboard with delay to ensure everything is set up
                def navigate_to_dashboard(dt):
                    self.root.current = 'dashboard'
                
                Clock.schedule_once(navigate_to_dashboard, 0.3)
                
            else:
                # Still navigate to dashboard but with error handling
                self.root.current = "dashboard"
            
        except Exception as e:
            print(f"Error handling successful login: {e}")
            # Still navigate to dashboard, but there might be issues
            self.root.current = "dashboard"

    def handle_logout(self):
        """Handle user logout - clean up user context"""
        try:
            
            # Get current user ID before clearing auth
            user_data = self.auth_service.get_user_data()
            current_user_id = user_data.get('id') if user_data else None
            
            # Logout from auth service (this clears user data)
            self.auth_service.logout()
            
            # Clear database sessions
            self.db_service.clear_all_sessions()
            
            # Reset dashboard
            dashboard_screen = self.get_dashboard_screen()
            if dashboard_screen:
                dashboard_screen.reset_for_new_user()
            
            # Update display name
            self.update_user_display_name()
            
            # Navigate to login
            self.root.current = "login"
            
            print("User logout handled successfully")
            
        except Exception as e:
            print(f"Error handling logout: {e}")
            # Still navigate to login
            self.root.current = "login"

    def get_dashboard_screen(self):
        """Get reference to dashboard screen"""
        try:
            for screen in self.root.screens:
                if screen.name == 'dashboard':
                    return screen
            return None
        except Exception as e:
            print(f"Error getting dashboard screen: {e}")
            return None

    def on_user_context_change(self):
        """Called when user context changes (login/logout)"""
        try:
            dashboard_screen = self.get_dashboard_screen()
            if dashboard_screen:
                dashboard_screen.force_refresh_for_user_change()
        except Exception as e:
            print(f"Error handling user context change: {e}")

    def update_user_display_name(self):
        """Fetches user data and updates the display name property."""
        if self.auth_service.is_authenticated():
            user_data = self.auth_service.get_user_data()
            
            if user_data:
                username = user_data.get('username')
                first_name = user_data.get('first_name')

                if username:
                    self.user_display_name = username
                elif first_name:
                    self.user_display_name = first_name
                else:
                    self.user_display_name = "User"
            else:
                self.user_display_name = "User"
        else:
            self.user_display_name = "Guest"
        
        # Force update all topbars in all screens
        try:
            self._update_all_topbars()
        except Exception as e:
            print(f"Error updating topbars: {e}")
    
    def _update_all_topbars(self):
        """Update all topbars in all screens"""
        if not hasattr(self, 'root') or not self.root:
            return
        
        # Check all screens in the screen manager
        if hasattr(self.root, 'screens'):
            for screen in self.root.screens:
                if hasattr(screen, 'ids') and hasattr(screen.ids, 'top_bar'):
                    screen.ids.top_bar.update_user_display()
        
        # Also check if there are any direct children with topbars
        if hasattr(self.root, 'children'):
            for child in self.root.children:
                if hasattr(child, 'ids') and hasattr(child.ids, 'top_bar'):
                    child.ids.top_bar.update_user_display()

    def on_pause(self):
        # Handle app pause (Android)
        return True
    
    def on_resume(self):
        # Handle app resume (Android)
        pass

if __name__ == '__main__':
    ResearchCollectorApp().run() 