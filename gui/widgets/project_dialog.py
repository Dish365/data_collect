from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
from kivymd.uix.label import MDLabel

try:
    Builder.load_file("kv/project_dialog.kv")
    print("ProjectDialog KV file loaded successfully")
except Exception as e:
    print(f"Error loading ProjectDialog KV file: {e}")

class ProjectDialog(MDBoxLayout):
    name_char_count = StringProperty("0/100")
    desc_char_count = StringProperty("0/500")
    is_name_valid = BooleanProperty(False)
    is_desc_valid = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("ProjectDialog initialized")
        
        # Apply responsive sizing after initialization
        Clock.schedule_once(self.apply_responsive_sizing, 0.1)
        
        # Bind character count updates
        Clock.schedule_once(self.setup_character_counting, 0.2)
    
    def setup_character_counting(self, dt):
        """Setup character counting for text fields"""
        try:
            if hasattr(self.ids, 'name_field'):
                self.ids.name_field.bind(text=self.on_name_text_change)
            if hasattr(self.ids, 'desc_field'):
                self.ids.desc_field.bind(text=self.on_desc_text_change)
            
            # Setup button validation
            self.setup_button_validation()
            
        except Exception as e:
            print(f"Error setting up character counting: {e}")
    
    def setup_button_validation(self):
        """Setup button validation and callbacks"""
        try:
            if hasattr(self.ids, 'save_button'):
                # Bind to validation changes
                self.bind(is_name_valid=self.on_validation_change)
                self.bind(is_desc_valid=self.on_validation_change)
                
                # Ensure initial white text
                self.ensure_save_button_white_text()
                
        except Exception as e:
            print(f"Error setting up button validation: {e}")
    
    def ensure_save_button_white_text(self):
        """Ensure save button text is always white"""
        try:
            if hasattr(self.ids, 'save_button'):
                for child in self.ids.save_button.children:
                    if hasattr(child, 'text_color'):
                        child.text_color = (1, 1, 1, 1)  # Always white text
        except Exception as e:
            print(f"Error ensuring save button white text: {e}")
    
    def on_validation_change(self, instance, value):
        """Update save button based on validation"""
        try:
            if hasattr(self.ids, 'save_button'):
                is_valid = self.is_valid()
                self.ids.save_button.disabled = not is_valid
                
                if is_valid:
                    self.ids.save_button.md_bg_color = (0.2, 0.6, 1, 1)  # Blue
                else:
                    self.ids.save_button.md_bg_color = (0.7, 0.7, 0.7, 1)  # Gray
                
                # Always ensure white text for save button
                for child in self.ids.save_button.children:
                    if hasattr(child, 'text_color'):
                        child.text_color = (1, 1, 1, 1)  # Always white text
                    
        except Exception as e:
            print(f"Error in validation change: {e}")
    
    def set_save_callback(self, callback):
        """Set the save button callback"""
        try:
            if hasattr(self.ids, 'save_button'):
                self.ids.save_button.bind(on_release=callback)
        except Exception as e:
            print(f"Error setting save callback: {e}")
    
    def set_cancel_callback(self, callback):
        """Set the cancel button callback"""
        try:
            if hasattr(self.ids, 'cancel_button'):
                self.ids.cancel_button.bind(on_release=callback)
        except Exception as e:
            print(f"Error setting cancel callback: {e}")
    
    def get_save_button(self):
        """Get the save button widget"""
        return self.ids.save_button if hasattr(self.ids, 'save_button') else None
    
    def get_cancel_button(self):
        """Get the cancel button widget"""
        return self.ids.cancel_button if hasattr(self.ids, 'cancel_button') else None
    
    def on_name_text_change(self, instance, value):
        """Handle name field text changes"""
        try:
            name = value.strip()
            char_count = len(name)
            self.name_char_count = f"{char_count}/100"
            
            # Validate name
            self.is_name_valid = self.validate_name_internal(name)
            
        except Exception as e:
            print(f"Error in name text change: {e}")
    
    def on_desc_text_change(self, instance, value):
        """Handle description field text changes"""
        try:
            desc = value.strip()
            char_count = len(desc)
            self.desc_char_count = f"{char_count}/500"
            
            # Validate description
            self.is_desc_valid = self.validate_description_internal(desc)
            
        except Exception as e:
            print(f"Error in desc text change: {e}")
    
    def validate_name_internal(self, name):
        """Internal validation for name field"""
        if not name:
            return False
        if len(name) > 100:
            return False
        if len(name) < 2:
            return False
        return True
    
    def validate_description_internal(self, description):
        """Internal validation for description field"""
        if len(description) > 500:
            return False
        return True
    
    def apply_responsive_sizing(self, dt):
        """Apply responsive sizing based on device category"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            
            category = ResponsiveHelper.get_screen_size_category()
            
            # Calculate minimum height needed for content (removed validation section)
            base_height = dp(180)  # Reduced base height without validation indicators
            spacing_height = dp(24)  # Height for spacing between sections
            
            # Adjust dialog dimensions based on device category
            if category == "large_tablet":
                content_height = base_height + spacing_height
                self.height = max(content_height, dp(280))
                self.spacing = dp(24)
                self.padding = dp(32)
                self._set_field_sizes(dp(64), dp(160), "18sp")
            elif category == "tablet":
                content_height = base_height + spacing_height
                self.height = max(content_height, dp(240))
                self.spacing = dp(20)
                self.padding = dp(24)
                self._set_field_sizes(dp(56), dp(140), "16sp")
            elif category == "small_tablet":
                content_height = base_height + spacing_height
                self.height = max(content_height, dp(220))
                self.spacing = dp(18)
                self.padding = dp(20)
                self._set_field_sizes(dp(52), dp(120), "15sp")
            else:  # phone
                content_height = base_height + spacing_height
                self.height = max(content_height, dp(200))
                self.spacing = dp(16)
                self.padding = dp(16)
                self._set_field_sizes(dp(48), dp(100), "14sp")
                
            print(f"ProjectDialog: Applied responsive sizing for {category} - Height: {self.height}")
            
        except Exception as e:
            print(f"Error applying responsive sizing to project dialog: {e}")
            # Fallback to default tablet sizing with proper height
            self.height = dp(240)
            self._set_field_sizes(dp(56), dp(140), "16sp")
    
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
            "is_valid": bool(name) and self.is_name_valid and self.is_desc_valid
        }

    def set_data(self, name="", description="", **kwargs):
        """Set dialog data"""
        try:
            self.ids.name_field.text = name
            self.ids.desc_field.text = description
            
            # Update character counts
            self.on_name_text_change(None, name)
            self.on_desc_text_change(None, description)
            
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
            self.is_name_valid = False
            self.is_desc_valid = True
        except Exception as e:
            print(f"Error resetting project dialog: {e}")
    
    def validate_name(self):
        """Validate project name field with enhanced feedback"""
        try:
            name = self.ids.name_field.text.strip()
            
            if not name:
                self.ids.name_field.error = True
                self.ids.name_field.helper_text = "Project name is required"
                return False
            elif len(name) < 2:
                self.ids.name_field.error = True
                self.ids.name_field.helper_text = "Project name must be at least 2 characters"
                return False
            elif len(name) > 100:
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
        """Validate project description field with enhanced feedback"""
        try:
            description = self.ids.desc_field.text.strip()
            
            if len(description) > 500:
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
        return self.validate_name() and self.validate_description() and self.is_name_valid and self.is_desc_valid
