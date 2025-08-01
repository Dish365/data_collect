from kivy.properties import BooleanProperty, StringProperty
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout

# KV file loaded by main app after theme initialization

class ProjectDialog(MDBoxLayout):
    """Modern responsive project dialog content widget for KivyMD 2.0"""
    
    is_valid_project = BooleanProperty(False)
    validation_message = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.projects_screen = None  # Reference to parent screen
        self.save_button = None  # Reference to save button
        self.dialog = None  # Reference to parent dialog
        
        # Apply responsive styling on creation
        self.apply_responsive_styling()
        
        # Bind validation events after initialization
        self.bind_validation_events()
    
    def apply_responsive_styling(self):
        """Apply simple responsive styling"""
        try:
            # Simple responsive spacing - keep it minimal
            from widgets.responsive_layout import ResponsiveHelper
            screen_category = ResponsiveHelper.get_screen_size_category()
            
            if screen_category == ResponsiveHelper.PHONE:
                self.spacing = dp(12)
            else:
                self.spacing = dp(16)
                
        except Exception as e:
            print(f"Error applying responsive styling: {e}")
            self.spacing = dp(16)  # Fallback
    
    def bind_save_button(self, save_button):
        """Bind the save button for validation updates"""
        self.save_button = save_button
        self.bind_validation_events()
    
    def bind_validation_events(self):
        """Bind validation events to text fields"""
        # Wait for ids to be available
        from kivy.clock import Clock
        Clock.schedule_once(self._delayed_bind, 0.1)
    
    def _delayed_bind(self, dt):
        """Delayed binding of validation events and auto-focus"""
        try:
            if hasattr(self.ids, 'name_field') and self.ids.name_field:
                self.ids.name_field.bind(text=self.on_name_change)
                self.ids.name_field.bind(on_text_validate=self.on_enter_pressed)
                # Auto-focus the first field for better UX
                self.ids.name_field.focus = True
            if hasattr(self.ids, 'desc_field') and self.ids.desc_field:
                self.ids.desc_field.bind(text=self.on_description_change)
            
            # Perform initial validation - but don't trigger errors initially
            self.is_valid_project = False
            
        except Exception as e:
            print(f"Error binding validation events: {e}")
            # Don't let validation errors break the dialog
    
    def on_name_change(self, instance, value):
        """Handle name field changes"""
        try:
            self.validate_all()
            self._update_save_button()
        except Exception as e:
            print(f"Error in name validation: {e}")
    
    def on_description_change(self, instance, value):
        """Handle description field changes"""
        try:
            self.validate_all()
            self._update_save_button()
        except Exception as e:
            print(f"Error in description validation: {e}")
    
    def on_enter_pressed(self, instance):
        """Handle Enter key press for better keyboard UX"""
        try:
            if self.is_valid():
                # Auto-save when Enter is pressed and form is valid
                self.on_save_pressed()
            elif hasattr(self.ids, 'desc_field') and self.ids.desc_field:
                # Move focus to description field if name is invalid
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: setattr(self.ids.desc_field, 'focus', True), 0.1)
        except Exception as e:
            print(f"Error handling Enter key: {e}")
    
    def validate_name(self):
        """Validate project name field"""
        try:
            if not hasattr(self.ids, 'name_field') or not self.ids.name_field:
                return False
                
            name = self.ids.name_field.text.strip() if self.ids.name_field.text else ""
            
            if not name:
                self.set_validation_error("Project name is required")
                return False
            
            if len(name) < 2:
                self.set_validation_error("Project name must be at least 2 characters")
                return False
            
            if len(name) > 100:
                self.set_validation_error("Project name is too long (max 100 characters)")
                return False
            
            # Check for invalid characters
            invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
            if any(char in name for char in invalid_chars):
                self.set_validation_error("Project name contains invalid characters")
                return False
            
            return True
        except Exception as e:
            print(f"Error validating name: {e}")
            return False
    
    def validate_description(self):
        """Validate project description field"""
        try:
            if not hasattr(self.ids, 'desc_field') or not self.ids.desc_field:
                return True
                
            description = self.ids.desc_field.text.strip() if self.ids.desc_field.text else ""
            
            if len(description) > 500:
                self.set_validation_error("Description is too long (max 500 characters)")
                return False
            
            return True
        except Exception as e:
            print(f"Error validating description: {e}")
            return True  # Description is optional, so default to valid
    
    def validate_all(self):
        """Validate all fields and update overall validation state"""
        try:
            name_valid = self.validate_name()
            desc_valid = self.validate_description()
            
            if name_valid and desc_valid:
                self.is_valid_project = True
                self.clear_validation_error()
            else:
                self.is_valid_project = False
            
            return self.is_valid_project
        except Exception as e:
            print(f"Error in validate_all: {e}")
            self.is_valid_project = False
            return False
    
    def set_validation_error(self, message):
        """Set validation error message"""
        try:
            self.validation_message = message
            if hasattr(self.ids, 'validation_label'):
                self.ids.validation_label.text = message
            if hasattr(self.ids, 'validation_container'):
                self.ids.validation_container.opacity = 1
        except Exception as e:
            print(f"Error setting validation error: {e}")
    
    def clear_validation_error(self):
        """Clear validation error message"""
        try:
            self.validation_message = ""
            if hasattr(self.ids, 'validation_label'):
                self.ids.validation_label.text = ""
            if hasattr(self.ids, 'validation_container'):
                self.ids.validation_container.opacity = 0
        except Exception as e:
            print(f"Error clearing validation error: {e}")
    
    def get_data(self):
        """Get dialog data for saving"""
        try:
            name = self.ids.name_field.text.strip() if hasattr(self.ids, 'name_field') else ""
            description = self.ids.desc_field.text.strip() if hasattr(self.ids, 'desc_field') else ""
            
            return {
                'name': name,
                'description': description,
                'is_valid': self.is_valid_project
            }
        except Exception as e:
            print(f"Error getting dialog data: {e}")
            return {'name': "", 'description': "", 'is_valid': False}
    
    def set_data(self, **kwargs):
        """Set dialog data for editing"""
        try:
            if hasattr(self.ids, 'name_field'):
                self.ids.name_field.text = kwargs.get('name', '')
                # Focus the name field for editing
                self.ids.name_field.focus = True
            
            if hasattr(self.ids, 'desc_field'):
                self.ids.desc_field.text = kwargs.get('description', '')
            
            # Re-validate after setting data
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.validate_all(), 0.1)
            
        except Exception as e:
            print(f"Error setting dialog data: {e}")
    
    def is_valid(self):
        """Check if dialog data is valid"""
        return self.validate_all()
    
    def clear_form(self):
        """Clear all form fields"""
        try:
            if hasattr(self.ids, 'name_field'):
                self.ids.name_field.text = ""
            
            if hasattr(self.ids, 'desc_field'):
                self.ids.desc_field.text = ""
            
            self.clear_validation_error()
            self.is_valid_project = False
            
        except Exception as e:
            print(f"Error clearing form: {e}")
    
    def focus_first_field(self):
        """Focus the first input field"""
        try:
            if hasattr(self.ids, 'name_field'):
                self.ids.name_field.focus = True
                if self.ids.name_field.text:
                    self.ids.name_field.cursor = (len(self.ids.name_field.text), 0)
        except Exception as e:
            print(f"Error focusing first field: {e}")
    
    def get_validation_summary(self):
        """Get a summary of validation issues"""
        issues = []
        
        if not self.validate_name():
            issues.append("Invalid project name")
        
        if not self.validate_description():
            issues.append("Invalid project description")
        
        return issues
    
    def _update_save_button(self):
        """Update save button state based on validation"""
        try:
            if hasattr(self.ids, 'save_btn') and self.ids.save_btn:
                self.ids.save_btn.disabled = not self.is_valid_project
        except Exception as e:
            print(f"Error updating save button: {e}")
    
    def on_cancel_pressed(self):
        """Handle cancel button press"""
        try:
            if self.dialog:
                self.dialog.dismiss()
            elif self.projects_screen and hasattr(self.projects_screen, 'close_dialog'):
                self.projects_screen.close_dialog()
        except Exception as e:
            print(f"Error handling cancel press: {e}")
    
    def on_save_pressed(self):
        """Handle save button press"""
        try:
            if not self.is_valid():
                return
            
            if self.projects_screen and hasattr(self.projects_screen, 'save_project'):
                # Pass a dummy instance to maintain compatibility with existing save_project method
                self.projects_screen.save_project(None)
            else:
                print("No projects screen reference or save method available")
        except Exception as e:
            print(f"Error handling save press: {e}")
    
    def set_dialog_reference(self, dialog):
        """Set reference to parent dialog"""
        self.dialog = dialog