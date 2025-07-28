from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty
from kivy.event import EventDispatcher
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from datetime import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window

# Load the KV file
Builder.load_file("kv/project_item.kv")


class ProjectItem(MDCard, EventDispatcher):
    """Modern project item widget using KivyMD 2.0.1 Material Design"""
    
    project_id = StringProperty('')
    name = StringProperty('')
    description = StringProperty('')
    created_at = StringProperty('')
    sync_status = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_edit')
        self.register_event_type('on_delete')
        self.register_event_type('on_build_form')
        
        # Setup responsive properties
        self.update_responsive_properties()
        
        # Bind to window resize for responsive updates
        Window.bind(on_resize=self._on_window_resize)
        
        # Bind properties for updates
        self.bind(name=self._update_name)
        self.bind(description=self._update_description)
        self.bind(created_at=self._update_date)
        self.bind(sync_status=self._update_sync_status)
        self.bind(size=self._update_text_sizes)
        self.bind(pos=self._update_text_sizes)

        # Populate initial data
        self._update_date(self, self.created_at)
        self._update_sync_status(self, self.sync_status)
    
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
                self.height = dp(96)
                self.padding = [dp(16), dp(16), dp(12), dp(16)]
                self.spacing = dp(20)
            elif category == "tablet":
                self.height = dp(84)
                self.padding = [dp(12), dp(12), dp(8), dp(12)]
                self.spacing = dp(16)
            elif category == "small_tablet":
                self.height = dp(78)
                self.padding = [dp(10), dp(10), dp(6), dp(10)]
                self.spacing = dp(14)
            else:  # phone
                self.height = dp(72)
                self.padding = [dp(8), dp(8), dp(4), dp(8)]
                self.spacing = dp(12)
                
        except Exception as e:
            print(f"Error updating ProjectItem responsive properties: {e}")
            # Fallback to default values
            self.height = dp(72)
            self.padding = [dp(8), dp(8), dp(4), dp(8)]
            self.spacing = dp(12)

    def _update_name(self, instance, value):
        """Update name label"""
        if hasattr(self, 'name_label'):
            self.name_label.text = value
            self._update_text_sizes()

    def _update_description(self, instance, value):
        """Update description label"""
        if hasattr(self, 'desc_label'):
            self.desc_label.text = value
            self._update_text_sizes()
    
    def _update_date(self, instance, value):
        """Update date labels"""
        if not value:
            if hasattr(self, 'day_label'):
                self.day_label.text = "--"
            if hasattr(self, 'month_label'):
                self.month_label.text = "N/A"
            return
            
        try:
            if '.' in value:
                dt_object = datetime.fromisoformat(value.split('.')[0])
            else:
                dt_object = datetime.fromisoformat(value.replace('Z', ''))
            
            if hasattr(self, 'day_label'):
                self.day_label.text = dt_object.strftime("%d")
            if hasattr(self, 'month_label'):
                self.month_label.text = dt_object.strftime("%b").upper()
        except (ValueError, TypeError):
            if hasattr(self, 'day_label'):
                self.day_label.text = "!"
            if hasattr(self, 'month_label'):
                self.month_label.text = "Err"

    def _update_sync_status(self, instance, value):
        """Update sync status label"""
        status_map = {
            'synced': ('Synced', (0.0, 0.6, 0.2, 1)),   # Green
            'pending': ('Pending', (0.9, 0.6, 0, 1)),   # Amber
            'failed': ('Failed', (0.8, 0, 0, 1)),       # Red
            'unknown': ('Unknown', (0.5, 0.5, 0.5, 1))  # Grey
        }

        label_text, color = status_map.get(value.lower(), status_map['unknown'])

        if hasattr(self, 'sync_status_label'):
            self.sync_status_label.text = label_text
            self.sync_status_label.theme_text_color = 'Custom'
            self.sync_status_label.text_color = color

    def _update_text_sizes(self, *args):
        """Update text sizes to enable proper ellipses truncation"""
        try:
            # Calculate available width for text
            total_width = self.width
            date_circle_width = self.get_date_circle_size()[0]
            right_layout_width = self.get_sync_status_size()[0] + self.get_menu_button_size()[0] + self.get_right_layout_spacing()
            padding_width = self.padding[0] + self.padding[2]  # left + right padding
            spacing_width = self.spacing * 2  # spacing between elements
            
            # Calculate available width for info layout
            available_width = total_width - date_circle_width - right_layout_width - padding_width - spacing_width
            
            # Set text_size for name and description labels
            if available_width > 0:
                # Name gets more space (about 60% of available width)
                name_width = available_width * 0.6
                if hasattr(self, 'name_label'):
                    self.name_label.text_size = (name_width, None)
                
                # Description gets the remaining space (about 40% of available width)
                desc_width = available_width * 0.4
                if hasattr(self, 'desc_label'):
                    self.desc_label.text_size = (desc_width, None)
            else:
                # Fallback if width calculation fails
                if hasattr(self, 'name_label'):
                    self.name_label.text_size = (200, None)
                if hasattr(self, 'desc_label'):
                    self.desc_label.text_size = (150, None)
                
        except Exception as e:
            print(f"Error updating text sizes: {e}")
            # Fallback values
            if hasattr(self, 'name_label'):
                self.name_label.text_size = (200, None)
            if hasattr(self, 'desc_label'):
                self.desc_label.text_size = (150, None)

    def get_date_circle_size(self):
        """Get responsive date circle size"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            category = ResponsiveHelper.get_screen_size_category()
            
            if category == "large_tablet":
                return (dp(72), dp(72))
            elif category == "tablet":
                return (dp(64), dp(64))
            elif category == "small_tablet":
                return (dp(60), dp(60))
            else:
                return (dp(56), dp(56))
        except Exception:
            return (dp(56), dp(56))

    def get_date_circle_radius(self):
        """Get responsive date circle radius"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            category = ResponsiveHelper.get_screen_size_category()
            
            if category == "large_tablet":
                return dp(36)
            elif category == "tablet":
                return dp(32)
            elif category == "small_tablet":
                return dp(30)
            else:
                return dp(28)
        except Exception:
            return dp(28)

    def get_date_circle_padding(self):
        """Get responsive date circle padding"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            category = ResponsiveHelper.get_screen_size_category()
            
            if category in ["tablet", "large_tablet"]:
                return dp(6)
            else:
                return dp(4)
        except Exception:
            return dp(4)

    def get_date_layout_spacing(self):
        """Get responsive date layout spacing"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            category = ResponsiveHelper.get_screen_size_category()
            
            if category in ["tablet", "large_tablet"]:
                return dp(4)
            else:
                return dp(2)
        except Exception:
            return dp(2)

    def get_info_layout_spacing(self):
        """Get responsive info layout spacing"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            category = ResponsiveHelper.get_screen_size_category()
            
            if category in ["tablet", "large_tablet"]:
                return dp(6)
            else:
                return dp(4)
        except Exception:
            return dp(4)

    def get_name_font_size(self):
        """Get responsive name font size"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            category = ResponsiveHelper.get_screen_size_category()
            
            if category == "large_tablet":
                return "20sp"
            elif category == "tablet":
                return "18sp"
            elif category == "small_tablet":
                return "16sp"
            else:
                return "14sp"
        except Exception:
            return "14sp"

    def get_description_font_size(self):
        """Get responsive description font size"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            category = ResponsiveHelper.get_screen_size_category()
            
            if category == "large_tablet":
                return "16sp"
            elif category == "tablet":
                return "15sp"
            elif category == "small_tablet":
                return "14sp"
            else:
                return "13sp"
        except Exception:
            return "13sp"

    def get_right_layout_spacing(self):
        """Get responsive right layout spacing"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            category = ResponsiveHelper.get_screen_size_category()
            
            if category in ["tablet", "large_tablet"]:
                return dp(12)
            else:
                return dp(8)
        except Exception:
            return dp(8)

    def get_sync_status_size(self):
        """Get responsive sync status label size"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            category = ResponsiveHelper.get_screen_size_category()
            
            if category == "large_tablet":
                return (dp(88), dp(32))
            elif category == "tablet":
                return (dp(80), dp(28))
            elif category == "small_tablet":
                return (dp(76), dp(26))
            else:
                return (dp(72), dp(24))
        except Exception:
            return (dp(72), dp(24))

    def get_sync_status_font_size(self):
        """Get responsive sync status font size"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            category = ResponsiveHelper.get_screen_size_category()
            
            if category == "large_tablet":
                return "14sp"
            elif category == "tablet":
                return "13sp"
            elif category == "small_tablet":
                return "12sp"
            else:
                return "11sp"
        except Exception:
            return "11sp"

    def get_menu_button_size(self):
        """Get responsive menu button size"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            category = ResponsiveHelper.get_screen_size_category()
            
            if category == "large_tablet":
                return (dp(56), dp(56))
            elif category == "tablet":
                return (dp(52), dp(52))
            elif category == "small_tablet":
                return (dp(48), dp(48))
            else:
                return (dp(44), dp(44))
        except Exception:
            return (dp(44), dp(44))

    def get_menu_icon_size(self):
        """Get responsive menu icon size"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            category = ResponsiveHelper.get_screen_size_category()
            
            if category == "large_tablet":
                return "28sp"
            elif category == "tablet":
                return "24sp"
            elif category == "small_tablet":
                return "22sp"
            else:
                return "20sp"
        except Exception:
            return "20sp"

    def open_menu(self, button):
        """Open the options menu"""
        if hasattr(self, 'menu'):
            self.menu.open()

    def on_edit(self, *args):
        """Handle edit event"""
        if hasattr(self, 'menu'):
            self.menu.dismiss()
    
    def on_delete(self, *args):
        """Handle delete event"""
        if hasattr(self, 'menu'):
            self.menu.dismiss()

    def on_build_form(self, *args):
        """Handle build form event"""
        if hasattr(self, 'menu'):
            self.menu.dismiss()
