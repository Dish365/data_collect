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
from kivy.clock import Clock

# KV file loaded by main app after theme initialization


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
        
        self.menu = None  # Initialize menu reference
        
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

        # Schedule initial data population
        Clock.schedule_once(self._populate_initial_data, 0.1)
    
    def _populate_initial_data(self, dt):
        """Populate initial data after widget is fully created"""
        self._update_date(self, self.created_at)
        self._update_sync_status(self, self.sync_status)
        self._update_text_sizes()
    
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
                self.height = dp(112)
                self.padding = [dp(28), dp(28), dp(24), dp(28)]
                self.spacing = dp(32)
            elif category == "tablet":
                self.height = dp(104)
                self.padding = [dp(28), dp(24), dp(24), dp(24)]
                self.spacing = dp(28)
            elif category == "small_tablet":
                self.height = dp(96)
                self.padding = [dp(24), dp(20), dp(20), dp(20)]
                self.spacing = dp(24)
            else:  # phone
                self.height = dp(88)
                self.padding = [dp(20), dp(16), dp(16), dp(16)]
                self.spacing = dp(20)
                
        except Exception as e:
            # Fallback to default values
            self.height = dp(104)
            self.padding = [dp(28), dp(24), dp(24), dp(24)]
            self.spacing = dp(28)

    def _update_name(self, instance, value):
        """Update name label"""
        if hasattr(self.ids, 'name_label'):
            self.ids.name_label.text = value
            Clock.schedule_once(lambda dt: self._update_text_sizes(), 0.1)

    def _update_description(self, instance, value):
        """Update description label"""
        if hasattr(self.ids, 'desc_label'):
            self.ids.desc_label.text = value
            Clock.schedule_once(lambda dt: self._update_text_sizes(), 0.1)
    
    def _update_date(self, instance, value):
        """Update date labels"""
        if not value:
            if hasattr(self.ids, 'day_label'):
                self.ids.day_label.text = "--"
            if hasattr(self.ids, 'month_label'):
                self.ids.month_label.text = "N/A"
            return
            
        try:
            if '.' in value:
                dt_object = datetime.fromisoformat(value.split('.')[0])
            else:
                dt_object = datetime.fromisoformat(value.replace('Z', ''))
            
            if hasattr(self.ids, 'day_label'):
                self.ids.day_label.text = dt_object.strftime("%d")
            if hasattr(self.ids, 'month_label'):
                self.ids.month_label.text = dt_object.strftime("%b").upper()
        except (ValueError, TypeError):
            if hasattr(self.ids, 'day_label'):
                self.ids.day_label.text = "!"
            if hasattr(self.ids, 'month_label'):
                self.ids.month_label.text = "Err"

    def _update_sync_status(self, instance, value):
        """Update sync status label and icon with modern styling"""
        status_config = {
            'synced': {
                'text': 'Synced', 
                'icon': 'check-circle-outline',
                'bg_color': (0.2, 0.7, 0.3, 0.15), 
                'text_color': (0.1, 0.6, 0.2, 1),
                'icon_color': (0.1, 0.6, 0.2, 1)
            },
            'pending': {
                'text': 'Pending', 
                'icon': 'clock-outline',
                'bg_color': (0.9, 0.7, 0.1, 0.15), 
                'text_color': (0.8, 0.5, 0.0, 1),
                'icon_color': (0.8, 0.5, 0.0, 1)
            },
            'failed': {
                'text': 'Failed', 
                'icon': 'alert-circle-outline',
                'bg_color': (0.9, 0.3, 0.3, 0.15), 
                'text_color': (0.8, 0.2, 0.2, 1),
                'icon_color': (0.8, 0.2, 0.2, 1)
            },
            'unknown': {
                'text': 'Unknown', 
                'icon': 'help-circle-outline',
                'bg_color': (0.6, 0.6, 0.6, 0.15), 
                'text_color': (0.5, 0.5, 0.5, 1),
                'icon_color': (0.5, 0.5, 0.5, 1)
            }
        }

        config = status_config.get(value.lower(), status_config['unknown'])

        if hasattr(self.ids, 'sync_status_label'):
            self.ids.sync_status_label.text = config['text']
            self.ids.sync_status_label.theme_text_color = 'Custom'
            self.ids.sync_status_label.text_color = config['text_color']
        
        if hasattr(self.ids, 'sync_status_icon'):
            self.ids.sync_status_icon.icon = config['icon']
            self.ids.sync_status_icon.theme_icon_color = 'Custom'
            self.ids.sync_status_icon.icon_color = config['icon_color']
            
        # Update parent card background color
        if hasattr(self.ids, 'sync_status_label'):
            status_card = self.ids.sync_status_label.parent.parent  # Go up to the MDCard
            if status_card:
                status_card.md_bg_color = config['bg_color']

    def _update_text_sizes(self, *args):
        """Update text sizes to enable proper ellipses truncation"""
        try:
            # Calculate available width for text labels
            if self.width <= 0:
                return
                
            # Fixed widths for date circle and right section
            date_circle_width = dp(56)
            right_section_width = dp(128)  # status label + menu button + spacing
            padding_and_spacing = dp(40)  # total padding and spacing
            
            # Calculate available width for info section
            available_width = self.width - date_circle_width - right_section_width - padding_and_spacing
            
            if available_width > 50:  # Minimum width check
                # Set responsive text sizes
                name_width = max(available_width * 0.7, 100)
                desc_width = max(available_width * 0.6, 80)
                
                # Update through ids if available
                if hasattr(self.ids, 'name_label'):
                    self.ids.name_label.text_size = (name_width, None)
                if hasattr(self.ids, 'desc_label'):
                    self.ids.desc_label.text_size = (desc_width, None)
                
        except Exception as e:
            print(f"Error updating text sizes: {e}")

























    def open_menu(self, button):
        """Open the options menu"""
        try:
            menu_items = [
                {
                    "text": "Edit Project",
                    "leading_icon": "pencil",
                    "on_release": lambda: self.dispatch('on_edit')
                },
                {
                    "text": "Build Form",
                    "leading_icon": "form-select",
                    "on_release": lambda: self.dispatch('on_build_form')
                },
                {
                    "text": "Delete Project",
                    "leading_icon": "delete",
                    "on_release": lambda: self.dispatch('on_delete')
                },
            ]
            
            self.menu = MDDropdownMenu(
                caller=button,
                items=menu_items,
                position="bottom",
                width=dp(200)
            )
            self.menu.open()
            
        except Exception as e:
            print(f"Error opening project menu: {e}")

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
