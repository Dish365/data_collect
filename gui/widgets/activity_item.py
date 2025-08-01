from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, BooleanProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp

# Load the KV file
# KV file loaded by main app after theme initialization


class ActivityItem(MDCard):
    """Modern activity item widget using KivyMD 2.0.1 Material Design"""
    
    activity_text = StringProperty("")
    activity_time = StringProperty("")
    activity_icon = StringProperty("information")
    is_team_activity = BooleanProperty(False)
    activity_type = StringProperty("")
    
    # Add properties that KV file is expecting
    title = StringProperty("")
    icon = StringProperty("information")
    
    def __init__(self, activity_text="", activity_time="", activity_icon="information", activity_type="", **kwargs):
        super().__init__(**kwargs)
        self.activity_text = activity_text
        self.activity_time = activity_time
        self.activity_icon = activity_icon
        self.activity_type = activity_type
        self.is_team_activity = activity_type == 'team_member'
        
        # Set KV properties - use activity_text as title for now
        self.title = activity_text
        self.icon = activity_icon
        
        # Setup responsive properties
        self.update_responsive_properties()
        
        # Bind to window resize for responsive updates
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, *args):
        """Handle window resize for responsive updates"""
        self.update_responsive_properties()
    
    def update_responsive_properties(self):
        """Update properties based on screen size"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            
            category = ResponsiveHelper.get_screen_size_category()
            
            # Responsive sizing based on device category
            if category == "large_tablet":
                self.height = dp(80)
                self.padding = [dp(16), dp(12)]
                self.spacing = dp(16)
            elif category == "tablet":
                self.height = dp(72)
                self.padding = [dp(14), dp(10)]
                self.spacing = dp(14)
            elif category == "small_tablet":
                self.height = dp(68)
                self.padding = [dp(12), dp(8)]
                self.spacing = dp(12)
            else:  # phone
                self.height = dp(64)
                self.padding = [dp(10), dp(6)]
                self.spacing = dp(10)
                
        except Exception as e:
            print(f"Error updating ActivityItem responsive properties: {e}")
            # Fallback to default values
            self.height = dp(64)
            self.padding = [dp(10), dp(6)]
            self.spacing = dp(10)
    
    def update_activity(self, text, time, icon="information", activity_type=""):
        """Update activity item with new data"""
        self.activity_text = text
        self.activity_time = time
        self.activity_icon = icon
        self.activity_type = activity_type
        self.is_team_activity = activity_type == 'team_member'
        
        # Update KV properties
        self.title = text
        self.icon = icon 