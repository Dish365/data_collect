from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from utils.toast import toast
from kivymd.app import MDApp
from kivy.properties import BooleanProperty
from kivy.core.window import Window
from kivy.clock import Clock
from widgets.responsive_layout import ResponsiveHelper
import re
import json

Builder.load_file("kv/signup.kv")

class SignUpScreen(MDScreen):
    password_visible = BooleanProperty(False)
    confirm_password_visible = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.on_window_resize)
        
    def on_window_resize(self, window, width, height):
        """Handle window resize to update responsive elements"""
        Clock.schedule_once(lambda dt: self.update_responsive_elements(), 0.1)
        
    def update_responsive_elements(self):
        """Update responsive elements based on current screen size"""
        if not self.ids:
            return
            
        try:
            # Update field heights and fonts based on screen size
            if Window.width > 600:
                button_height = "56dp"
                field_height = "56dp"
                button_font_size = "18sp"
                field_font_size = "16sp"
            else:
                button_height = "48dp"
                field_height = "48dp"
                button_font_size = "16sp"
                field_font_size = "14sp"
                
            # Update signup button
            if hasattr(self.ids, 'signup_button') and self.ids.signup_button:
                self.ids.signup_button.height = button_height
                self.ids.signup_button.font_size = button_font_size
                
            # Update all text fields
            field_ids = ['username', 'first_name', 'last_name', 'email', 'institution', 'password', 'confirm_password']
            for field_id in field_ids:
                try:
                    if hasattr(self.ids, field_id) and self.ids[field_id]:
                        field = self.ids[field_id]
                        field.height = field_height
                        field.font_size = field_font_size
                except Exception as e:
                    print(f"Error updating field {field_id}: {e}")
                    
        except Exception as e:
            print(f"Error updating responsive elements: {e}")
    
    def clear_all_fields(self):
        """Clear all input fields to show placeholders"""
        field_ids = ['username', 'first_name', 'last_name', 'email', 'institution', 'password', 'confirm_password']
        for field_id in field_ids:
            try:
                if hasattr(self.ids, field_id) and self.ids[field_id]:
                    self.ids[field_id].text = ""
                    # Force refresh of hint text
                    self.ids[field_id].focus = False
            except Exception as e:
                print(f"Error clearing field {field_id}: {e}")
    
    def toggle_password_visibility(self):
        """Toggle password field visibility"""
        print("Toggling password visibility (signup)")
        self.password_visible = not self.password_visible
        try:
            if hasattr(self.ids, 'password') and self.ids.password:
                self.ids.password.password = not self.password_visible
                print("Password field updated:", self.ids.password.password)
        except Exception as e:
            print("Error updating password field:", e)
    
    def toggle_confirm_password_visibility(self):
        """Toggle confirm password field visibility"""
        print("Toggling confirm password visibility (signup)")
        self.confirm_password_visible = not self.confirm_password_visible
        try:
            if hasattr(self.ids, 'confirm_password') and self.ids.confirm_password:
                self.ids.confirm_password.password = not self.confirm_password_visible
                print("Confirm password field updated:", self.ids.confirm_password.password)
        except Exception as e:
            print("Error updating confirm password field:", e)
    
    def get_form_data(self):
        """Safely get form data from all fields"""
        try:
            return {
                'username': self.ids.username.text.strip() if self.ids.username else "",
                'first_name': self.ids.first_name.text.strip() if self.ids.first_name else "",
                'last_name': self.ids.last_name.text.strip() if self.ids.last_name else "",
                'email': self.ids.email.text.strip() if self.ids.email else "",
                'institution': self.ids.institution.text.strip() if self.ids.institution else "",
                'password': self.ids.password.text if self.ids.password else "",
                'confirm_password': self.ids.confirm_password.text if self.ids.confirm_password else ""
            }
        except Exception as e:
            print(f"Error getting form data: {e}")
            return {}
    
    def signup(self):
        """Handle signup with global loading and proper validation"""
        try:
            # Get form data safely
            form_data = self.get_form_data()
            if not form_data:
                toast("Error reading form data. Please try again.")
                return
            
            # Validate input
            validation_result = self._validate_form(**form_data)
            if not validation_result['valid']:
                toast(validation_result['message'])
                return
            
            # Show global loading
            app = MDApp.get_running_app()
            app.show_global_loading("Creating account...")
            
            # Get auth service and register
            app.auth_service.register(
                username=form_data['username'],
                email=form_data['email'],
                password=form_data['password'],
                password2=form_data['confirm_password'],
                first_name=form_data['first_name'],
                last_name=form_data['last_name'],
                institution=form_data['institution'],
                role="researcher",
                callback=self._on_registration_complete
            )
            
        except Exception as e:
            print(f"Error during signup: {e}")
            app = MDApp.get_running_app()
            app.hide_global_loading()
            toast("An error occurred during registration. Please try again.")
    
    def _validate_form(self, username, first_name, last_name, email, institution, password, confirm_password):
        """Validate form input with detailed feedback"""
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
        
        # Validate names (letters, spaces, hyphens, apostrophes only)
        name_pattern = r"^[a-zA-Z\s\-']+$"
        if not re.match(name_pattern, first_name):
            return {'valid': False, 'message': 'First name can only contain letters, spaces, hyphens, and apostrophes'}
        
        if not re.match(name_pattern, last_name):
            return {'valid': False, 'message': 'Last name can only contain letters, spaces, hyphens, and apostrophes'}
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return {'valid': False, 'message': 'Please enter a valid email address'}
        
        # Validate institution (basic check for reasonable length)
        if len(institution.strip()) < 2:
            return {'valid': False, 'message': 'Institution name must be at least 2 characters'}
        
        # Validate password strength
        if len(password) < 8:
            return {'valid': False, 'message': 'Password must be at least 8 characters long'}
        
        # Check if password contains at least one letter and one number
        if not re.search(r'[a-zA-Z]', password):
            return {'valid': False, 'message': 'Password must contain at least one letter'}
        
        if not re.search(r'\d', password):
            return {'valid': False, 'message': 'Password must contain at least one number'}
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return {'valid': False, 'message': 'Password should contain at least one special character'}
        
        # Check if passwords match
        if password != confirm_password:
            return {'valid': False, 'message': 'Passwords do not match'}
        
        return {'valid': True}
    
    def _on_registration_complete(self, result):
        """Handle registration completion"""
        try:
            # Hide global loading
            app = MDApp.get_running_app()
            app.hide_global_loading()
            
            if result.get('success'):
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
                status_code = result.get('status_code')
                
                print(f"Registration failed - Error: {error_type}, Message: {message}, Status: {status_code}")
                
                # Handle different error types
                if error_type == 'network_unavailable' or error_type == 'network_error':
                    toast("No network connection. Please check your internet connection.")
                elif error_type == 'timeout':
                    toast("Request timed out. Please try again.")
                elif error_type == 'connection_error':
                    toast("Connection failed. Please check your internet connection.")
                elif status_code == 400:
                    # Handle validation errors from backend
                    if isinstance(message, dict):
                        # Extract field-specific errors
                        for field, errors in message.items():
                            if isinstance(errors, list) and errors:
                                field_name = field.replace('_', ' ').title()
                                toast(f"{field_name}: {errors[0]}")
                                return
                            elif isinstance(errors, str):
                                field_name = field.replace('_', ' ').title()
                                toast(f"{field_name}: {errors}")
                                return
                        # If no specific field errors, show general message
                        toast("Please check your input and try again.")
                    else:
                        toast("Invalid registration data. Please check your input.")
                elif status_code == 409 or 'already exists' in str(message).lower():
                    toast("User with this username or email already exists")
                elif status_code == 500:
                    toast("Server error. Please try again later.")
                else:
                    # Generic error handling
                    if isinstance(message, dict):
                        # Try to extract meaningful error message
                        error_msg = str(message.get('detail', message.get('error', message)))
                    else:
                        error_msg = str(message)
                    toast(f"Registration failed: {error_msg}")
                    
        except Exception as e:
            print(f"Error handling registration completion: {e}")
            self.is_registering = False
            toast("An error occurred. Please try again.")
    
    def on_login(self):
        """Navigate to login screen"""
        try:
            
            self.manager.transition.direction = "right"
            self.manager.current = "login"
        except Exception as e:
            print(f"Error navigating to login: {e}")
    
        def on_enter(self):
            """Called when screen is entered"""
        try:
            # Clear previous input and errors to show placeholders
            self.clear_all_fields()
            
            self.password_visible = False
            self.confirm_password_visible = False
            
            # Update responsive elements with slight delay
            Clock.schedule_once(lambda dt: self.update_responsive_elements(), 0.1)
            
        except Exception as e:
            print(f"Error in on_enter: {e}")
        
    def on_kv_post(self, base_widget):
        """Called after KV file is loaded"""
        try:
            super().on_kv_post(base_widget)
            
            # Update responsive elements
            Clock.schedule_once(lambda dt: self.update_responsive_elements(), 0.1)
            
            # Clear all fields to show placeholders
            Clock.schedule_once(lambda dt: self.clear_all_fields(), 0.2)
            
        except Exception as e:
            print(f"Error in on_kv_post: {e}")