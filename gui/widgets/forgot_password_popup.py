from kivy.uix.popup import Popup
from kivy.properties import BooleanProperty
from kivy.lang import Builder
from kivymd.app import MDApp
from utils.cross_platform_toast import toast

# KV file loaded by main app after theme initialization  # Adjust path if needed

class ForgotPasswordPopup(Popup):
    is_processing = BooleanProperty(False)

    def on_submit(self):
        """Handle password reset submission"""
        value = self.ids.user_input.text.strip()
        if not value:
            self.ids.info_label.text = "Please enter a username or email!"
            return
        
        # Start processing
        self.is_processing = True
        self.ids.info_label.text = "Processing your request..."
        
        # Get auth service and request password reset
        app = MDApp.get_running_app()
        app.auth_service.forgot_password(value, self._on_forgot_password_complete)
    
    def _on_forgot_password_complete(self, result):
        """Handle forgot password completion"""
        # Stop processing
        self.is_processing = False
        
        if result.get('success'):
            # Success
            message = result.get('message', 'Password reset instructions sent!')
            
            # Check if this is development mode with token in message
            if 'Password reset token:' in message:
                # Development mode - show token dialog
                self._show_token_dialog(message)
            else:
                # Production mode - just show success message
                toast(message)
                self.dismiss()
        else:
            # Error
            error_type = result.get('error')
            message = result.get('message', 'Password reset failed')
            
            if error_type == 'user_not_found':
                self.ids.info_label.text = "No user found with this username or email."
            elif error_type == 'network_unavailable' or error_type == 'network_error':
                self.ids.info_label.text = "No network connection. Please check your internet connection."
            elif error_type == 'timeout':
                self.ids.info_label.text = "Request timed out. Please try again."
            elif error_type == 'connection_error':
                self.ids.info_label.text = "Connection failed. Please check your internet connection."
            elif error_type == 'server_error':
                self.ids.info_label.text = f"Server error: {message}"
            else:
                self.ids.info_label.text = f"Error: {message}"
    
    def _show_token_dialog(self, message):
        """Show development token dialog"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        
        # Extract token from message
        token = message.split('Password reset token: ')[1].split(' ')[0]
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing="10dp",
            size_hint_y=None,
            height="200dp"
        )
        
        content.add_widget(MDLabel(
            text="Development Mode: Reset Token Generated",
                            font_style="Title",
                role="medium",
            size_hint_y=None,
            height="30dp"
        ))
        
        content.add_widget(MDLabel(
            text="Use this token to reset your password:",
                            font_style="Body",
                role="large",
            size_hint_y=None,
            height="30dp"
        ))
        
        token_field = MDTextField(
            text=token,
            mode="rectangle",
            readonly=True,
            size_hint_y=None,
            height="40dp"
        )
        content.add_widget(token_field)
        
        new_password_field = MDTextField(
            hint_text="New Password",
            password=True,
            mode="rectangle",
            size_hint_y=None,
            height="40dp"
        )
        content.add_widget(new_password_field)
        
        confirm_password_field = MDTextField(
            hint_text="Confirm New Password", 
            password=True,
            mode="rectangle",
            size_hint_y=None,
            height="40dp"
        )
        content.add_widget(confirm_password_field)
        
        def reset_password():
            new_pass = new_password_field.text
            confirm_pass = confirm_password_field.text
            
            if not new_pass or not confirm_pass:
                toast("Please enter both password fields")
                return
                
            if new_pass != confirm_pass:
                toast("Passwords do not match")
                return
                
            if len(new_pass) < 8:
                toast("Password must be at least 8 characters")
                return
                
            # Call backend reset password endpoint
            app = MDApp.get_running_app()
            app.auth_service.reset_password_with_token(token, new_pass, confirm_pass, self._on_reset_complete)
            dialog.dismiss()
        
        dialog = MDDialog(
            title="Reset Password",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(text="Reset Password", on_release=lambda x: reset_password())
            ]
        )
        
        dialog.open()
        self.dismiss()  # Close the original popup
    
    def _on_reset_complete(self, result):
        """Handle password reset completion"""
        if result.get('success'):
            toast("Password reset successfully! Please log in with your new password.")
        else:
            toast(f"Password reset failed: {result.get('message', 'Unknown error')}")
