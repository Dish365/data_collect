from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton

Builder.load_file("kv/topbar.kv")

class TopBar(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logout_dialog = None
    
    def set_title(self, text):
        self.ids.top_title.text = text
    
    def logout(self):
        """Show logout confirmation dialog"""
        if not self.logout_dialog:
            self.logout_dialog = MDDialog(
                title="Confirm Logout",
                text="Are you sure you want to logout? All unsaved data will be lost.",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=self._dismiss_logout_dialog
                    ),
                    MDRaisedButton(
                        text="LOGOUT",
                        on_release=self._confirm_logout
                    ),
                ],
            )
        self.logout_dialog.open()
    
    def _dismiss_logout_dialog(self, instance):
        """Dismiss the logout confirmation dialog"""
        if self.logout_dialog:
            self.logout_dialog.dismiss()
    
    def _confirm_logout(self, instance):
        """Handle confirmed logout"""
        if self.logout_dialog:
            self.logout_dialog.dismiss()
        
        app = MDApp.get_running_app()
        
        # Logout from auth service
        app.auth_service.logout()
        app.user_display_name = "Guest"
        
        # Show logout message
        toast("Logged out successfully")
        
        # Navigate back to login screen
        app.root.transition.direction = "right"
        app.root.current = "login"
