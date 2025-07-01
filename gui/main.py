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


# Import screens
from screens.login import LoginScreen
from screens.dashboard import DashboardScreen
from screens.projects import ProjectsScreen
from screens.data_collection import DataCollectionScreen
from screens.analytics import AnalyticsScreen
from screens.form_builder import FormBuilderScreen
from screens.sync import SyncScreen
from screens.signup import SignUpScreen
from screens.responses import ResponsesScreen

from kivy.modules import inspector

# Import services
from services.database import DatabaseService
from services.sync_service import SyncService
from services.auth_service import AuthService
from services.form_service import FormService

class ResearchCollectorApp(MDApp):
    user_display_name = StringProperty("Guest")

    def build(self):
        self.theme_cls.primary_palette = "Blue"    
        self.theme_cls.primary_hue     = "500" 
        
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
        
        # Create screen manager
        sm = ScreenManager()
        
        # Add screens
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignUpScreen(name='signup'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(ProjectsScreen(name='projects'))
        sm.add_widget(DataCollectionScreen(name='data_collection'))
        sm.add_widget(AnalyticsScreen(name='analytics'))
        sm.add_widget(FormBuilderScreen(name='form_builder'))
        sm.add_widget(SyncScreen(name='sync'))
        sm.add_widget(ResponsesScreen(name='responses'))

        inspector.create_inspector(Window, sm)
        
        return sm
    
    def setup_responsive_window(self):
        """Setup responsive window sizing for tablet optimization"""
        try:
            # Get screen dimensions
            from tkinter import Tk
            root = Tk()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
            
            # Calculate optimal tablet window size (80% of screen for development)
            tablet_width = min(int(screen_width * 0.8), 1200)  # Max 1200px width
            tablet_height = min(int(screen_height * 0.8), 900)  # Max 900px height
            
            # Ensure minimum tablet-friendly dimensions
            tablet_width = max(tablet_width, 800)   # Minimum 800px width
            tablet_height = max(tablet_height, 600)  # Minimum 600px height
            
            Window.size = (tablet_width, tablet_height)
            Window.minimum_width = 800
            Window.minimum_height = 600
            
            print(f"Tablet window initialized: {tablet_width}x{tablet_height}")
            
        except Exception as e:
            # Fallback to default tablet size
            print(f"Could not detect screen size: {e}")
            Window.size = (1024, 768)  # Standard tablet landscape
            Window.minimum_width = 800
            Window.minimum_height = 600
    
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
        
    def handle_successful_login(self):
        """Handle successful login - set up user context and navigate to dashboard"""
        try:
            print("=== Handling successful login ===")
            self.update_user_display_name()
            
            # Get user data and set database context
            user_data = self.auth_service.get_user_data()
            if user_data and 'id' in user_data:
                user_id = user_data['id']
                print(f"Setting up session for user: {user_id}")
                
                # Set database user context
                self.db_service.set_current_user(user_id)
                
                # Clean up stale sync data to prevent incorrect counts
                self.db_service.cleanup_stale_sync_data()
                
                # Verify user data integrity
                self.db_service.ensure_user_data_integrity(user_id)
                
                # Verify database context was set correctly
                db_user = self.db_service.get_current_user()
                if db_user != user_id:
                    print(f"Warning: Database context mismatch after login. Expected: {user_id}, Got: {db_user}")
                    # Try setting it again
                    self.db_service.set_current_user(user_id)
                    db_user = self.db_service.get_current_user()
                    if db_user != user_id:
                        print(f"Error: Failed to establish database context for user {user_id}")
                
                # Reset dashboard for new user
                dashboard_screen = self.get_dashboard_screen()
                if dashboard_screen:
                    print("Resetting dashboard for new user")
                    dashboard_screen.reset_for_new_user()
                
                print(f"User session initialized successfully for: {user_id}")
                print(f"Database context verified: {db_user}")
                
                # Add a longer delay to ensure everything is set up
                def navigate_to_dashboard(dt):
                    print("Navigating to dashboard after initialization delay")
                    self.root.current = 'dashboard'
                
                Clock.schedule_once(navigate_to_dashboard, 0.3)  # Increased delay
                
            else:
                print("Warning: No user ID found in user data")
                # Still navigate to dashboard but with error handling
                self.root.current = "dashboard"
            
        except Exception as e:
            print(f"Error handling successful login: {e}")
            # Still navigate to dashboard, but there might be issues
            self.root.current = "dashboard"

    def handle_logout(self):
        """Handle user logout - clean up user context"""
        try:
            print("Handling user logout")
            
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

    def on_pause(self):
        # Handle app pause (Android)
        return True
    
    def on_resume(self):
        # Handle app resume (Android)
        pass

if __name__ == '__main__':
    ResearchCollectorApp().run() 