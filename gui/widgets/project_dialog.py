from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock

Builder.load_file("kv/project_dialog.kv")

class ProjectDialog(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Apply responsive sizing after initialization
        Clock.schedule_once(self.apply_responsive_sizing, 0.1)
    
    def apply_responsive_sizing(self, dt):
        """Apply responsive sizing based on device category"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            
            category = ResponsiveHelper.get_screen_size_category()
            
            # Adjust dialog dimensions based on device category
            if category == "large_tablet":
                self.height = dp(280)
                self.spacing = dp(24)
                self.padding = dp(32)
                self._set_field_sizes(dp(64), dp(140), "18sp")
            elif category == "tablet":
                self.height = dp(240)
                self.spacing = dp(20)
                self.padding = dp(24)
                self._set_field_sizes(dp(56), dp(120), "16sp")
            elif category == "small_tablet":
                self.height = dp(220)
                self.spacing = dp(18)
                self.padding = dp(20)
                self._set_field_sizes(dp(52), dp(100), "15sp")
            else:  # phone
                self.height = dp(180)
                self.spacing = dp(16)
                self.padding = dp(16)
                self._set_field_sizes(dp(48), dp(80), "14sp")
                
            print(f"ProjectDialog: Applied responsive sizing for {category}")
            
        except Exception as e:
            print(f"Error applying responsive sizing to project dialog: {e}")
            # Fallback to default tablet sizing
            self._set_field_sizes(dp(56), dp(120), "16sp")
    
    def _set_field_sizes(self, name_height, desc_height, font_size):
        """Set field sizes based on device category"""
        try:
            if hasattr(self.ids, 'name_field'):
                self.ids.name_field.height = name_height
                self.ids.name_field.font_size = font_size
                
            if hasattr(self.ids, 'desc_field'):
                self.ids.desc_field.height = desc_height
                self.ids.desc_field.font_size = font_size
                
        except Exception as e:
            print(f"Error setting field sizes: {e}")
    
    def get_data(self):
        """Get dialog data with validation"""
        name = self.ids.name_field.text.strip()
        description = self.ids.desc_field.text.strip()
        
        return {
            "name": name,
            "description": description,
            "is_valid": bool(name)  # Name is required
        }

    def set_data(self, name="", description="", **kwargs):
        """Set dialog data"""
        try:
            self.ids.name_field.text = name
            self.ids.desc_field.text = description
            
            def set_focus(dt):
                self.ids.name_field.focus = True
            Clock.schedule_once(set_focus, 0.2)
            
        except Exception as e:
            print(f"Error setting project dialog data: {e}")

    def reset(self):
        """Reset dialog to default state"""
        self.set_data()
        
        # Clear any validation states
        try:
            self.ids.name_field.error = False
            self.ids.desc_field.error = False
        except Exception as e:
            print(f"Error resetting project dialog: {e}")
    
    def validate_name(self):
        """Validate project name field"""
        try:
            name = self.ids.name_field.text.strip()
            
            if not name:
                self.ids.name_field.error = True
                self.ids.name_field.helper_text = "Project name is required"
                return False
            elif len(name) > 100:  # Reasonable limit
                self.ids.name_field.error = True
                self.ids.name_field.helper_text = "Project name too long (max 100 characters)"
                return False
            else:
                self.ids.name_field.error = False
                self.ids.name_field.helper_text = ""
                return True
                
        except Exception as e:
            print(f"Error validating project name: {e}")
            return False
    
    def validate_description(self):
        """Validate project description field"""
        try:
            description = self.ids.desc_field.text.strip()
            
            if len(description) > 500:  # Reasonable limit
                self.ids.desc_field.error = True
                self.ids.desc_field.helper_text = "Description too long (max 500 characters)"
                return False
            else:
                self.ids.desc_field.error = False
                self.ids.desc_field.helper_text = ""
                return True
                
        except Exception as e:
            print(f"Error validating project description: {e}")
            return True  # Description is optional
    
    def is_valid(self):
        """Check if entire dialog is valid"""
        return self.validate_name() and self.validate_description()
