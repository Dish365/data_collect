from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.toast import toast

Builder.load_file("kv/forgot_password_popup.kv")  # Adjust path if needed

class ForgotPasswordPopup(Popup):
    user_input = ObjectProperty(None)
    info_label = ObjectProperty(None)
    submit_callback = ObjectProperty(None)
    is_processing = BooleanProperty(False)

    def on_submit(self):
        """Handle password reset submission"""
        value = self.user_input.text.strip()
        if not value:
            self.info_label.text = "Please enter a username or email!"
            return
        
        # Start processing
        self.is_processing = True
        self.info_label.text = "Processing your request..."
        
        # Get auth service and request password reset
        app = MDApp.get_running_app()
        app.auth_service.forgot_password(value, self._on_forgot_password_complete)
    
    def _on_forgot_password_complete(self, result):
        """Handle forgot password completion"""
        # Stop processing
        self.is_processing = False
        
        if result.get('success'):
            # Success
            toast(result.get('message', 'Password reset instructions sent!'))
            self.dismiss()
        else:
            # Error
            error_type = result.get('error')
            message = result.get('message', 'Password reset failed')
            
            if error_type == 'user_not_found':
                self.info_label.text = "No user found with this username or email."
            elif error_type == 'network_unavailable':
                self.info_label.text = "No network connection. Please check your internet connection."
            elif error_type == 'timeout':
                self.info_label.text = "Request timed out. Please try again."
            elif error_type == 'connection_error':
                self.info_label.text = "Connection failed. Please check your internet connection."
            elif error_type == 'server_error':
                self.info_label.text = f"Server error: {message}"
            else:
                self.info_label.text = f"Error: {message}"
