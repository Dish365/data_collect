from kivy.metrics import dp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.app import App
import threading
import uuid
import json
from datetime import datetime

# KivyMD 2.0 imports
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel

# Import with fallbacks for better compatibility
try:
    from utils.cross_platform_toast import toast
except ImportError:
    def toast(message):
        print(f"Toast: {message}")

try:
    from widgets.loading_overlay import LoadingOverlay
except ImportError:
    print("Warning: LoadingOverlay widget not found")
    LoadingOverlay = None

try:
    from services.project_service import ProjectService
except ImportError:
    print("Warning: ProjectService not found")
    ProjectService = None

try:
    from widgets.responsive_layout import ResponsiveHelper
except ImportError:
    print("Warning: ResponsiveHelper not found")
    ResponsiveHelper = None

# KV file loaded by main app after theme initialization

class ProjectCreationScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        
        # Initialize services with fallbacks
        self.auth_service = getattr(app, 'auth_service', None)
        if ProjectService and hasattr(app, 'auth_service') and hasattr(app, 'db_service') and hasattr(app, 'sync_service'):
            self.project_service = ProjectService(app.auth_service, app.db_service, app.sync_service)
        else:
            print("Warning: ProjectService not available")
            self.project_service = None
            
        self.sync_service = getattr(app, 'sync_service', None)
        
        # Form state
        self.is_loading = False
        self.is_valid_form = False
        self.validation_errors = {}
        
        # Initialize loading overlay
        if LoadingOverlay:
            self.loading_overlay = LoadingOverlay()
        else:
            self.loading_overlay = None

    def on_enter(self):
        """Called when the screen is entered"""
        if hasattr(self.ids, 'top_bar') and self.ids.top_bar:
            self.ids.top_bar.set_title("Create New Project")
            self.ids.top_bar.set_current_screen("project_creation")
        
        # Update responsive layout
        self.update_responsive_layout()
        
        # Focus the first field
        Clock.schedule_once(self.focus_first_field, 0.2)
    
    def on_leave(self):
        """Called when leaving the screen"""
        # Clear form when leaving (optional)
        pass
    
    def update_responsive_layout(self):
        """Update layout based on screen size with enhanced responsive design"""
        try:
            if ResponsiveHelper:
                category = ResponsiveHelper.get_screen_size_category()
                
                # Adjust spacing and padding based on screen size
                if hasattr(self.ids, 'main_content'):
                    if category == ResponsiveHelper.PHONE:
                        self.ids.main_content.padding = [dp(16), dp(12), dp(16), dp(12)]
                        self.ids.main_content.spacing = dp(20)
                    elif category == ResponsiveHelper.SMALL_TABLET:
                        self.ids.main_content.padding = [dp(24), dp(16), dp(24), dp(16)]
                        self.ids.main_content.spacing = dp(24)
                    else:  # TABLET, LARGE_TABLET, DESKTOP
                        self.ids.main_content.padding = [dp(32), dp(24), dp(32), dp(24)]
                        self.ids.main_content.spacing = dp(28)
                
                # Adjust form field heights based on screen size
                if hasattr(self.ids, 'name_field'):
                    if category == ResponsiveHelper.PHONE:
                        self.ids.name_field.height = dp(64)
                    else:
                        self.ids.name_field.height = dp(72)
                
                if hasattr(self.ids, 'description_field'):
                    if category == ResponsiveHelper.PHONE:
                        self.ids.description_field.height = dp(120)
                    else:
                        self.ids.description_field.height = dp(140)
                
                # Adjust button sizes based on screen size
                if hasattr(self.ids, 'create_button'):
                    if category == ResponsiveHelper.PHONE:
                        self.ids.create_button.size = (dp(140), dp(44))
                        self.ids.cancel_button.size = (dp(100), dp(44))
                    else:
                        self.ids.create_button.size = (dp(160), dp(48))
                        self.ids.cancel_button.size = (dp(120), dp(48))
                        
        except Exception as e:
            print(f"Error updating responsive layout: {e}")
    
    def focus_first_field(self, dt=None):
        """Focus the first input field"""
        try:
            if hasattr(self.ids, 'name_field') and self.ids.name_field:
                self.ids.name_field.focus = True
        except Exception as e:
            print(f"Error focusing first field: {e}")
    
    def on_name_change(self, instance, value):
        """Handle name field changes"""
        try:
            self.validate_name()
            self.update_form_validity()
        except Exception as e:
            print(f"Error in name validation: {e}")
    
    def on_description_change(self, instance, value):
        """Handle description field changes"""
        try:
            self.validate_description()
            self.update_form_validity()
        except Exception as e:
            print(f"Error in description validation: {e}")
    
    def on_enter_pressed(self, instance):
        """Handle Enter key press for better keyboard UX"""
        try:
            if hasattr(self.ids, 'name_field') and instance == self.ids.name_field:
                if self.validate_name():
                    # Move to description field if name is valid
                    if hasattr(self.ids, 'description_field'):
                        Clock.schedule_once(
                            lambda dt: setattr(self.ids.description_field, 'focus', True), 
                            0.1
                        )
                    else:
                        # If no description field, try to create if form is valid
                        if self.is_valid():
                            self.on_create_pressed()
            elif hasattr(self.ids, 'description_field') and instance == self.ids.description_field:
                # From description field, create if valid
                if self.is_valid():
                    self.on_create_pressed()
                    
        except Exception as e:
            print(f"Error handling Enter key: {e}")
    
    def on_key_down(self, keyboard, keycode, text, modifiers):
        """Handle keyboard shortcuts"""
        try:
            key = keycode[1]
            
            # Ctrl+Enter or Cmd+Enter to create project
            if key == 'enter' and ('ctrl' in modifiers or 'cmd' in modifiers):
                if self.is_valid():
                    self.on_create_pressed()
                return True
            
            # Escape to cancel
            elif key == 'escape':
                self.on_cancel_pressed()
                return True
            
            return False
        except Exception as e:
            print(f"Error handling key down: {e}")
            return False
    
    def validate_name(self):
        """Validate project name field"""
        try:
            if not hasattr(self.ids, 'name_field') or not self.ids.name_field:
                return False
                
            name = self.ids.name_field.text.strip() if self.ids.name_field.text else ""
            
            if not name:
                self.set_field_error('name', "Project name is required")
                return False
            
            if len(name) < 2:
                self.set_field_error('name', "Project name must be at least 2 characters")
                return False
            
            if len(name) > 100:
                self.set_field_error('name', "Project name is too long (max 100 characters)")
                return False
            
            # Check for invalid characters
            invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
            if any(char in name for char in invalid_chars):
                self.set_field_error('name', "Project name contains invalid characters")
                return False
            
            self.clear_field_error('name')
            return True
        except Exception as e:
            print(f"Error validating name: {e}")
            return False
    
    def validate_description(self):
        """Validate project description field"""
        try:
            if not hasattr(self.ids, 'description_field') or not self.ids.description_field:
                return True
                
            description = self.ids.description_field.text.strip() if self.ids.description_field.text else ""
            
            if len(description) > 500:
                self.set_field_error('description', "Description is too long (max 500 characters)")
                return False
            
            self.clear_field_error('description')
            return True
        except Exception as e:
            print(f"Error validating description: {e}")
            return True  # Description is optional, so default to valid
    
    def set_field_error(self, field, message):
        """Set validation error for a specific field"""
        self.validation_errors[field] = message
        self.show_validation_error(message)
    
    def clear_field_error(self, field):
        """Clear validation error for a specific field"""
        if field in self.validation_errors:
            del self.validation_errors[field]
        
        if not self.validation_errors:
            self.clear_validation_error()
    
    def show_validation_error(self, message):
        """Show validation error message with animation"""
        try:
            if hasattr(self.ids, 'error_label'):
                self.ids.error_label.text = message
            if hasattr(self.ids, 'error_container'):
                # Animate error container appearance
                from kivy.animation import Animation
                self.ids.error_container.opacity = 0
                anim = Animation(opacity=1, duration=0.3, transition='out_cubic')
                anim.start(self.ids.error_container)
        except Exception as e:
            print(f"Error showing validation error: {e}")
    
    def clear_validation_error(self):
        """Clear validation error message with animation"""
        try:
            if hasattr(self.ids, 'error_container'):
                # Animate error container disappearance
                from kivy.animation import Animation
                anim = Animation(opacity=0, duration=0.2, transition='in_cubic')
                anim.start(self.ids.error_container)
                
                # Clear text after animation
                def clear_text(dt):
                    if hasattr(self.ids, 'error_label'):
                        self.ids.error_label.text = ""
                Clock.schedule_once(clear_text, 0.2)
        except Exception as e:
            print(f"Error clearing validation error: {e}")
    
    def update_form_validity(self):
        """Update overall form validity and save button state with animation"""
        try:
            name_valid = self.validate_name()
            desc_valid = self.validate_description()
            
            old_valid = self.is_valid_form
            self.is_valid_form = name_valid and desc_valid
            
            # Update save button state with animation if state changed
            if hasattr(self.ids, 'create_button'):
                self.ids.create_button.disabled = not self.is_valid_form
                
                # Add subtle animation when button becomes enabled/disabled
                if old_valid != self.is_valid_form:
                    from kivy.animation import Animation
                    if self.is_valid_form:
                        # Button enabled - animate with emphasis
                        anim = Animation(elevation=4, duration=0.2, transition='out_back')
                        anim += Animation(elevation=2, duration=0.1, transition='in_cubic')
                        anim.start(self.ids.create_button)
                    else:
                        # Button disabled - subtle fade
                        anim = Animation(elevation=0, duration=0.2, transition='in_cubic')
                        anim.start(self.ids.create_button)
                
        except Exception as e:
            print(f"Error updating form validity: {e}")
            self.is_valid_form = False
    
    def get_form_data(self):
        """Get form data"""
        try:
            name = self.ids.name_field.text.strip() if hasattr(self.ids, 'name_field') else ""
            description = self.ids.description_field.text.strip() if hasattr(self.ids, 'description_field') else ""
            
            return {
                'name': name,
                'description': description
            }
        except Exception as e:
            print(f"Error getting form data: {e}")
            return {'name': "", 'description': ""}
    
    def clear_form(self):
        """Clear all form fields"""
        try:
            if hasattr(self.ids, 'name_field'):
                self.ids.name_field.text = ""
            
            if hasattr(self.ids, 'description_field'):
                self.ids.description_field.text = ""
            
            self.clear_validation_error()
            self.validation_errors = {}
            self.is_valid_form = False
            
            # Update save button state
            if hasattr(self.ids, 'create_button'):
                self.ids.create_button.disabled = True
                
        except Exception as e:
            print(f"Error clearing form: {e}")
    
    def on_cancel_pressed(self):
        """Handle cancel button press - go back to projects screen"""
        try:
            app = App.get_running_app()
            if hasattr(app.root, 'current'):
                app.root.current = 'projects'
        except Exception as e:
            print(f"Error handling cancel press: {e}")
            toast("Error navigating back")
    
    def on_create_pressed(self):
        """Handle create button press"""
        try:
            if not self.is_valid_form:
                toast("Please fix form errors before creating project")
                return
            
            if self.is_loading:
                return
            
            # Show loading state
            self.set_loading_state(True)
            
            # Get form data
            form_data = self.get_form_data()
            
            # Create project in background thread
            threading.Thread(
                target=self._create_project_thread,
                args=(form_data,),
                daemon=True
            ).start()
            
        except Exception as e:
            print(f"Error handling create press: {e}")
            toast("Error creating project")
            self.set_loading_state(False)
    
    def _create_project_thread(self, form_data):
        """Create project in background thread"""
        try:
            if not self.project_service:
                Clock.schedule_once(lambda dt: self._on_create_error("Project service not available"), 0)
                return
            
            # Create project data
            project_data = {
                'id': str(uuid.uuid4()),
                'name': form_data['name'],
                'description': form_data['description'],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            # Save project
            success = self.project_service.create_project(project_data)
            
            if success:
                Clock.schedule_once(lambda dt: self._on_create_success(project_data), 0)
            else:
                Clock.schedule_once(lambda dt: self._on_create_error("Failed to create project"), 0)
                
        except Exception as e:
            print(f"Error in create project thread: {e}")
            Clock.schedule_once(lambda dt: self._on_create_error(f"Error: {str(e)}"), 0)
    
    def _on_create_success(self, project_data):
        """Handle successful project creation with celebration animation"""
        try:
            self.set_loading_state(False)
            
            # Success animation sequence
            self._animate_success_feedback(project_data)
            
        except Exception as e:
            print(f"Error handling create success: {e}")
    
    def _animate_success_feedback(self, project_data):
        """Animate success feedback before navigation"""
        try:
            from kivy.animation import Animation
            
            # Success message
            toast(f"Project '{project_data['name']}' created successfully!")
            
            # Animate create button success state
            if hasattr(self.ids, 'create_button'):
                # Change button to success state temporarily
                original_text = "Create Project"
                if hasattr(self.ids.create_button, 'children') and self.ids.create_button.children:
                    for child in self.ids.create_button.children:
                        if hasattr(child, 'text'):
                            child.text = "✓ Created!"
                
                # Success animation
                success_anim = Animation(
                    elevation=6, 
                    duration=0.3, 
                    transition='out_back'
                ) + Animation(
                    elevation=2, 
                    duration=0.2, 
                    transition='in_cubic'
                )
                success_anim.start(self.ids.create_button)
            
            # Animate form card success
            if hasattr(self.ids, 'main_content'):
                # Subtle success glow effect
                success_glow = Animation(
                    opacity=0.8, 
                    duration=0.2, 
                    transition='out_sine'
                ) + Animation(
                    opacity=1, 
                    duration=0.3, 
                    transition='in_sine'
                )
                success_glow.start(self.ids.main_content)
            
            # Schedule navigation after animation
            Clock.schedule_once(
                lambda dt: self._complete_success_navigation(project_data), 
                1.0
            )
            
        except Exception as e:
            print(f"Error in success animation: {e}")
            # Fallback to immediate navigation
            self._complete_success_navigation(project_data)
    
    def _complete_success_navigation(self, project_data):
        """Complete the success flow with navigation and form builder integration"""
        try:
            # Clear form
            self.clear_form()
            
            app = App.get_running_app()
            
            # Store the created project for form builder to pick up
            app._selected_project_for_form_builder = project_data
            
            # Navigate directly to form builder to start building forms
            if hasattr(app.root, 'current'):
                app.root.current = 'form_builder'
                
                # Also refresh projects list in the background if possible
                if hasattr(app.root, 'get_screen'):
                    try:
                        projects_screen = app.root.get_screen('projects')
                        if hasattr(projects_screen, 'refresh_projects'):
                            projects_screen.refresh_projects()
                    except:
                        pass  # Don't fail if projects screen doesn't exist
            
        except Exception as e:
            print(f"Error completing success navigation: {e}")
            # Fallback to projects screen
            try:
                app = App.get_running_app()
                if hasattr(app.root, 'current'):
                    app.root.current = 'projects'
            except:
                pass
    
    def _on_create_error(self, error_message):
        """Handle project creation error"""
        try:
            self.set_loading_state(False)
            toast(error_message)
        except Exception as e:
            print(f"Error handling create error: {e}")
    
    def set_loading_state(self, loading):
        """Set loading state and update UI"""
        try:
            self.is_loading = loading
            
            # Update create button
            if hasattr(self.ids, 'create_button'):
                self.ids.create_button.disabled = loading or not self.is_valid_form
            
            # Update cancel button
            if hasattr(self.ids, 'cancel_button'):
                self.ids.cancel_button.disabled = loading
            
            # Show/hide loading overlay
            if self.loading_overlay and hasattr(self.ids, 'main_content'):
                if loading:
                    if self.loading_overlay.parent != self.ids.main_content:
                        self.ids.main_content.add_widget(self.loading_overlay)
                    self.loading_overlay.show("Creating project...")
                else:
                    self.loading_overlay.hide()
                    if self.loading_overlay.parent:
                        self.loading_overlay.parent.remove_widget(self.loading_overlay)
            
        except Exception as e:
            print(f"Error setting loading state: {e}")