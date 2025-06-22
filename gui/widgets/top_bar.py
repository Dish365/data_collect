from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.toast import toast

Builder.load_file("kv/topbar.kv")

class TopBar(MDBoxLayout):
    def set_title(self, text):
        self.ids.top_title.text = text
    
    def logout(self):
        """Handle user logout"""
        app = MDApp.get_running_app()
        
        # Logout from auth service
        app.auth_service.logout()
        app.user_display_name = "Guest"
        
        # Show logout message
        toast("Logged out successfully")
        
        # Navigate back to login screen
        app.root.transition.direction = "right"
        app.root.current = "login"
