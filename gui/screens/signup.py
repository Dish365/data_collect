from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivymd.toast import toast
from kivymd.app import MDApp
from kivy.properties import BooleanProperty
import re
import json

Builder.load_file("kv/signup.kv")

class SignUpScreen(MDScreen):
    is_registering = BooleanProperty(False)
    password_visible = BooleanProperty(False)
    confirm_password_visible = BooleanProperty(False)
    
    def toggle_password_visibility(self):
        print("Toggling password visibility (signup)")
        self.password_visible = not self.password_visible
        try:
            print("Current password field:", self.ids.password)
            self.ids.password.password = not self.password_visible
            print("Password field updated:", self.ids.password.password)
        except Exception as e:
            print("Error updating password field:", e)
    
    def toggle_confirm_password_visibility(self):
        print("Toggling confirm password visibility (signup)")
        self.confirm_password_visible = not self.confirm_password_visible
        try:
            print("Current confirm password field:", self.ids.confirm_password)
            self.ids.confirm_password.password = not self.confirm_password_visible
            print("Confirm password field updated:", self.ids.confirm_password.password)
        except Exception as e:
            print("Error updating confirm password field:", e)
    
    def signup(self):
        """Handle signup with spinner and proper validation"""
        # Get form data
        username = self.ids.username.text.strip()
        first_name = self.ids.first_name.text.strip()
        last_name = self.ids.last_name.text.strip()
        email = self.ids.email.text.strip()
        institution = self.ids.institution.text.strip()
        password = self.ids.password.text
        confirm_password = self.ids.confirm_password.text
        
        # Validate input
        validation_result = self._validate_form(username, first_name, last_name, email, institution, password, confirm_password)
        if not validation_result['valid']:
            toast(validation_result['message'])
            return
        
        # Start registration process
        self.is_registering = True
        
        # Get auth service and register
        app = MDApp.get_running_app()
        app.auth_service.register(
            username=username,
            email=email,
            password=password,
            password2=confirm_password,
            first_name=first_name,
            last_name=last_name,
            institution=institution,
            role="researcher",
            callback=self._on_registration_complete
        )
    
    def _validate_form(self, username, first_name, last_name, email, institution, password, confirm_password):
        """Validate form input"""
        # Check if all required fields are filled
        if not username:
            return {'valid': False, 'message': 'Username is required'}
        
        if not first_name:
            return {'valid': False, 'message': 'First name is required'}
        
        if not last_name:
            return {'valid': False, 'message': 'Last name is required'}
        
        if not email:
            return {'valid': False, 'message': 'Email is required'}
        
        if not institution:
            return {'valid': False, 'message': 'Institution is required'}
        
        if not password:
            return {'valid': False, 'message': 'Password is required'}
        
        if not confirm_password:
            return {'valid': False, 'message': 'Please confirm your password'}
        
        # Validate username (alphanumeric and underscore only, 3-30 characters)
        if not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):
            return {'valid': False, 'message': 'Username must be 3-30 characters and contain only letters, numbers, and underscores'}
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return {'valid': False, 'message': 'Please enter a valid email address'}
        
        # Validate password strength
        if len(password) < 8:
            return {'valid': False, 'message': 'Password must be at least 8 characters long'}
        
        # Check if password contains at least one letter and one number
        if not re.search(r'[a-zA-Z]', password) or not re.search(r'\d', password):
            return {'valid': False, 'message': 'Password must contain at least one letter and one number'}
        
        # Check if passwords match
        if password != confirm_password:
            return {'valid': False, 'message': 'Passwords do not match'}
        
        return {'valid': True}
    
    def _on_registration_complete(self, result):
        """Handle registration completion"""
        # Stop spinner
        self.is_registering = False
        
        if result.get('success'):
            app = MDApp.get_running_app()
            data = result.get('data', {})
            token = data.get('token')
            user = data.get('user')
            if token and user:
                app.auth_service.token = token
                app.auth_service.user_data = user
                app.auth_service.store.put('auth', token=token, username=user.get('username', ''), user_data=json.dumps(user))
                app.update_user_display_name()  # Ensure display name is updated
            toast("Registration successful! Welcome to Research Data Collector!")
            self.manager.transition.direction = "left"
            self.manager.current = "dashboard"
            app.handle_successful_login()
        else:
            # Registration failed
            error_type = result.get('error')
            message = result.get('message', 'Registration failed')
            
            # Show appropriate error message
            if error_type == 'validation_error':
                # Show field-specific errors if available
                field_errors = result.get('field_errors', {})
                if field_errors:
                    # Show first field error
                    for field, errors in field_errors.items():
                        if isinstance(errors, list) and errors:
                            toast(f"{field.title()}: {errors[0]}")
                            break
                else:
                    toast(message)
            elif error_type == 'user_exists':
                toast("User with this username or email already exists")
            elif error_type == 'network_unavailable':
                toast("No network connection. Please check your internet connection.")
            elif error_type == 'timeout':
                toast("Request timed out. Please try again.")
            elif error_type == 'connection_error':
                toast("Connection failed. Please check your internet connection.")
            elif error_type == 'server_error':
                toast(f"Server error: {message}")
            else:
                toast(f"Registration failed: {message}")
    
    def on_login(self):
        """Navigate to login screen"""
        if not self.is_registering:
            self.manager.transition.direction = "right"
            self.manager.current = "login"
    
    def on_enter(self):
        """Called when screen is entered"""
        # Clear previous input and errors
        self.ids.username.text = ""
        self.ids.first_name.text = ""
        self.ids.last_name.text = ""
        self.ids.email.text = ""
        self.ids.institution.text = ""
        self.ids.password.text = ""
        self.ids.confirm_password.text = ""
        self.is_registering = False
        self.password_visible = False
        self.confirm_password_visible = False