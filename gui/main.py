import os
os.environ['KIVY_LOG_MODE'] = 'PYTHON'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.utils import platform

# Import screens
from screens.login import LoginScreen
from screens.dashboard import DashboardScreen
from screens.projects import ProjectsScreen
from screens.data_collection import DataCollectionScreen
from screens.analytics import AnalyticsScreen
from screens.form_builder import FormBuilderScreen
from screens.sync import SyncScreen

# Import services
from services.database import DatabaseService
from services.sync_service import SyncService
from services.auth_service import AuthService

class ResearchCollectorApp(App):
    def build(self):
        # Set window size for development
        if platform != 'android':
            Window.size = (768, 1024)
        
        # Initialize services
        self.db_service = DatabaseService()
        self.sync_service = SyncService()
        self.auth_service = AuthService()
        
        # Create screen manager
        sm = ScreenManager()
        
        # Add screens
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(ProjectsScreen(name='projects'))
        sm.add_widget(DataCollectionScreen(name='data_collection'))
        sm.add_widget(AnalyticsScreen(name='analytics'))
        sm.add_widget(FormBuilderScreen(name='form_builder'))
        sm.add_widget(SyncScreen(name='sync'))
        
        return sm
    
    def on_start(self):
        # Initialize database
        self.db_service.init_database()
        
    def on_pause(self):
        # Handle app pause (Android)
        return True
    
    def on_resume(self):
        # Handle app resume (Android)
        pass

if __name__ == '__main__':
    ResearchCollectorApp().run() 