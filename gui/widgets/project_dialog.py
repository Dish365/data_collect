from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout

# Load the KV file
Builder.load_file("kv/project_dialog.kv")

class ProjectDialog(MDBoxLayout):
    """Modern project dialog content widget for KivyMD 2.0"""
    
    is_valid_project = BooleanProperty(False)
    validation_message = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Bind validation events after initialization
        self.bind_validation_events()
    
    def bind_validation_events(self):
        """Bind validation events to text fields"""
        # Wait for ids to be available
        from kivy.clock import Clock
        Clock.schedule_once(self._delayed_bind, 0.1)
    
    def _delayed_bind(self, dt):
        """Delayed binding of validation events"""
        try:
            if hasattr(self.ids, 'name_field'):
                self.ids.name_field.bind(text=self.on_name_change)
            if hasattr(self.ids, 'desc_field'):
                self.ids.desc_field.bind(text=self.on_description_change)
            
            # Perform initial validation
            self.validate_all()
            
        except Exception as e:
            print(f"Error binding validation events: {e}")
    
    def on_name_change(self, instance, value):
        """Handle name field changes"""
        self.validate_name()
        self.validate_all()
    
    def on_description_change(self, instance, value):
        """Handle description field changes"""
        self.validate_description()
        self.validate_all()
    
    def validate_name(self):
        """Validate project name field"""
        if not hasattr(self.ids, 'name_field'):
            return False
            
        name = self.ids.name_field.text.strip()
        
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
    
    def validate_description(self):
        """Validate project description field"""
        if not hasattr(self.ids, 'desc_field'):
            return True
            
        description = self.ids.desc_field.text.strip()
        
        if len(description) > 500:
            self.set_validation_error("Description is too long (max 500 characters)")
            return False
        
        return True
    
    def validate_all(self):
        """Validate all fields and update overall validation state"""
        name_valid = self.validate_name()
        desc_valid = self.validate_description()
        
        if name_valid and desc_valid:
            self.is_valid_project = True
            self.clear_validation_error()
        else:
            self.is_valid_project = False
        
        return self.is_valid_project
    
    def set_validation_error(self, message):
        """Set validation error message"""
        self.validation_message = message
        if hasattr(self.ids, 'validation_label'):
            self.ids.validation_label.text = message
            self.ids.validation_label.opacity = 1
    
    def clear_validation_error(self):
        """Clear validation error message"""
        self.validation_message = ""
        if hasattr(self.ids, 'validation_label'):
            self.ids.validation_label.text = ""
            self.ids.validation_label.opacity = 0
    
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
            return {
                'name': "",
                'description': "",
                'is_valid': False
            }
    
    def set_data(self, **kwargs):
        """Set dialog data for editing"""
        try:
            if hasattr(self.ids, 'name_field'):
                self.ids.name_field.text = kwargs.get('name', '')
            
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