import os
os.environ['KIVY_LOG_MODE'] = 'PYTHON'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.app import MDApp
from kivy.properties import StringProperty


# Import screens
from screens.login import LoginScreen
from screens.dashboard import DashboardScreen
from screens.projects import ProjectsScreen
from screens.data_collection import DataCollectionScreen
from screens.analytics import AnalyticsScreen
from screens.form_builder import FormBuilderScreen
from screens.sync import SyncScreen
from screens.signup import SignUpScreen

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
        # Set window size for development
        if platform != 'android':
            Window.size = (768, 924)
        
        # Initialize services
        self.db_service = DatabaseService()
        self.sync_service = SyncService(self.db_service)
        self.auth_service = AuthService()
        self.form_service = FormService(self.auth_service, self.db_service, self.sync_service)
        
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

        inspector.create_inspector(Window, sm)
        
        return sm
    
    def on_start(self):
        """Called when app starts"""
        # Initialize database
        self.db_service.init_database()
        
        # Migrate existing data to include user_id fields
        self.db_service.migrate_existing_data()
        
        # Check if user is already authenticated
        if self.auth_service.is_authenticated():
            self.update_user_display_name()
            # User is already logged in, go to dashboard
            self.root.current = "dashboard"
        else:
            # User needs to login
            self.root.current = "login"
        
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