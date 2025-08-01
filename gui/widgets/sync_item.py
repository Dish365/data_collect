from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, ObjectProperty
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.core.window import Window
from datetime import datetime

# Load the KV file
# KV file loaded by main app after theme initialization


class SyncItem(MDCard):
    """Modern sync item widget using KivyMD 2.0.1 Material Design"""
    
    table_name = StringProperty("")
    operation = StringProperty("")
    record_id = StringProperty("")
    created_at = StringProperty("")
    attempts = StringProperty("0")
    status = StringProperty("pending")
    sync_data = ObjectProperty()
    
    def __init__(self, sync_data, on_sync_pressed=None, **kwargs):
        super().__init__(**kwargs)
        self.sync_data = sync_data
        self.on_sync_pressed = on_sync_pressed
        
        # Setup responsive properties
        self.update_responsive_properties()
        
        # Bind to window resize for responsive updates
        Window.bind(on_resize=self._on_window_resize)
        
        # Update properties from sync_data
        self._update_from_sync_data()
        
        # Bind properties
        self.bind(sync_data=self._update_from_sync_data)
    
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
                self.height = dp(140)
                self.padding = [dp(16), dp(12)]
                self.spacing = dp(16)
            elif category == "tablet":
                self.height = dp(130)
                self.padding = [dp(14), dp(10)]
                self.spacing = dp(14)
            elif category == "small_tablet":
                self.height = dp(125)
                self.padding = [dp(12), dp(8)]
                self.spacing = dp(12)
            else:  # phone
                self.height = dp(120)
                self.padding = [dp(10), dp(6)]
                self.spacing = dp(10)
                
        except Exception as e:
            print(f"Error updating SyncItem responsive properties: {e}")
            # Fallback to default values
            self.height = dp(120)
            self.padding = [dp(10), dp(6)]
            self.spacing = dp(10)
    
    def _update_from_sync_data(self, *args):
        """Update properties from sync_data"""
        if not self.sync_data:
            return
            
        self.table_name = self.sync_data.get('table_name', '')
        self.operation = self.sync_data.get('operation', '')
        self.record_id = self.sync_data.get('record_id', '')
        self.attempts = str(self.sync_data.get('attempts', 0))
        self.status = self.sync_data.get('status', 'pending')
        
        # Format created date
        created_date = self.sync_data.get('created_at', '')
        if created_date:
            try:
                if isinstance(created_date, str):
                    dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d %H:%M')
                else:
                    formatted_date = created_date.strftime('%Y-%m-%d %H:%M')
            except:
                formatted_date = str(created_date)
        else:
            formatted_date = "Unknown"
        
        self.created_at = formatted_date
    
    def on_sync_button_pressed(self, instance):
        """Handle sync button press"""
        if self.on_sync_pressed:
            self.on_sync_pressed(self.sync_data)
    
    def update_status(self, status):
        """Update the status of this sync item"""
        self.sync_data['status'] = status
        self.status = status
        # Refresh the UI
        self._update_from_sync_data()
    
 