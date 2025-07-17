from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.event import EventDispatcher
from kivy.clock import Clock
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDListItem
from datetime import datetime
from kivy.app import App
from kivy.lang import Builder

# Load the KV file for this widget
Builder.load_file("kv/project_item.kv")


class ProjectItem(MDCard, EventDispatcher):
    """
    Modern Project Item widget using KivyMD 2.0+ approach
    
    This widget displays project information in a card format with:
    - Date circle showing creation date
    - Project name and description
    - Sync status indicator
    - Options menu for actions
    """
    
    # Properties for data binding
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
        
        # Setup responsive layout
        self.setup_responsive_layout()
        
        # Create dropdown menu after widgets are created
        Clock.schedule_once(self.create_menu, 0)
        
        # Bind property changes to UI updates
        self.bind(name=self._update_name)
        self.bind(description=self._update_description)
        self.bind(created_at=self._update_date)
        self.bind(sync_status=self._update_sync_status)
        
        # Populate initial data after widgets are ready
        Clock.schedule_once(lambda dt: self._update_date(self, self.created_at), 0)
        Clock.schedule_once(lambda dt: self._update_sync_status(self, self.sync_status), 0)

    def setup_responsive_layout(self):
        """Setup responsive layout properties based on screen size"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            
            category = ResponsiveHelper.get_screen_size_category()
            
            # Set responsive properties based on device category
            if category == "large_tablet":
                self.orientation = 'horizontal'
                self.padding = (dp(16), dp(16), dp(12), dp(16))
                self.spacing = dp(20)
                self.size_hint_y = None
                self.height = dp(96)
                self.elevation = 1.2
            elif category == "tablet":
                self.orientation = 'horizontal'
                self.padding = (dp(12), dp(12), dp(8), dp(12))
                self.spacing = dp(16)
                self.size_hint_y = None
                self.height = dp(84)
                self.elevation = 1.0
            elif category == "small_tablet":
                self.orientation = 'horizontal'
                self.padding = (dp(10), dp(10), dp(6), dp(10))
                self.spacing = dp(14)
                self.size_hint_y = None
                self.height = dp(78)
                self.elevation = 0.9
            else:  # phone
                self.orientation = 'horizontal'
                self.padding = (dp(8), dp(8), dp(4), dp(8))
                self.spacing = dp(12)
                self.size_hint_y = None
                self.height = dp(72)
                self.elevation = 0.8
                
        except Exception as e:
            print(f"Error setting up responsive layout for project item: {e}")
            # Fallback to original sizing
            self.orientation = 'horizontal'
            self.padding = (dp(8), dp(8), dp(4), dp(8))
            self.spacing = dp(12)
            self.size_hint_y = None
            self.height = dp(72)
            self.elevation = 0.8

    def create_menu(self, dt=None):
        """Create the dropdown menu for project actions"""
        try:
            # Get the menu button reference from the KV file
            menu_button = self.ids.menu_button if hasattr(self, 'ids') else None
            
            if not menu_button:
                print("Warning: Menu button not found, skipping menu creation")
                return
                
            # Use the latest KivyMD approach for menu items
            menu_items = [
                {
                    "text": "Edit",
                    "on_release": self.on_edit_pressed
                },
                {
                    "text": "Build Form", 
                    "on_release": self.on_build_form_pressed
                },
                {
                    "text": "Delete", 
                    "on_release": self.on_delete_pressed
                },
            ]
            
            self.menu = MDDropdownMenu(
                caller=menu_button,
                items=menu_items,
                width_mult=4,
                position="auto"
            )
        except Exception as e:
            print(f"Error creating menu: {e}")
            # Fallback: create menu without items
            if menu_button:
                self.menu = MDDropdownMenu(
                    caller=menu_button,
                    items=[],
                    width_mult=4,
                    position="auto"
                )

    def is_tablet(self):
        """Check if current device is a tablet"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            category = ResponsiveHelper.get_screen_size_category()
            return category in ["small_tablet", "tablet", "large_tablet"]
        except Exception:
            return False

    def get_date_circle_size(self):
        """Get responsive date circle size"""
        if self.is_tablet():
            return dp(56), dp(56)
        return dp(48), dp(48)

    def get_date_circle_radius(self):
        """Get responsive date circle radius"""
        if self.is_tablet():
            return dp(28)
        return dp(24)

    def get_date_circle_padding(self):
        """Get responsive date circle padding"""
        if self.is_tablet():
            return dp(8), dp(8), dp(8), dp(8)
        return dp(6), dp(6), dp(6), dp(6)

    def get_date_layout_spacing(self):
        """Get responsive date layout spacing"""
        if self.is_tablet():
            return dp(2)
        return dp(1)

    def get_info_layout_spacing(self):
        """Get responsive info layout spacing"""
        if self.is_tablet():
            return dp(8)
        return dp(6)

    def get_name_font_size(self):
        """Get responsive name font size"""
        if self.is_tablet():
            return "20sp"
        return "16sp"

    def get_description_font_size(self):
        """Get responsive description font size"""
        if self.is_tablet():
            return "16sp"
        return "14sp"

    def get_right_layout_spacing(self):
        """Get responsive right layout spacing"""
        if self.is_tablet():
            return dp(12)
        return dp(8)

    def get_sync_status_size(self):
        """Get responsive sync status size"""
        if self.is_tablet():
            return dp(80), dp(24)
        return dp(60), dp(20)

    def get_sync_status_font_size(self):
        """Get responsive sync status font size"""
        if self.is_tablet():
            return "14sp"
        return "12sp"

    def get_menu_button_size(self):
        """Get responsive menu button size"""
        if self.is_tablet():
            return dp(40), dp(40)
        return dp(32), dp(32)

    def get_menu_icon_size(self):
        """Get responsive menu icon size"""
        if self.is_tablet():
            return "24sp"
        return "20sp"

    def open_menu(self, button):
        """Open the dropdown menu"""
        if hasattr(self, 'menu') and self.menu:
            try:
                # Close any existing menu first
                if self.menu.state == "open":
                    self.menu.dismiss()
                else:
                    self.menu.open()
            except Exception as e:
                print(f"Error opening menu: {e}")
                # Try to recreate the menu if it fails
                try:
                    Clock.schedule_once(self.create_menu, 0.1)
                except:
                    pass

    def on_edit_pressed(self):
        """Handle edit button press"""
        if hasattr(self, 'menu') and self.menu:
            self.menu.dismiss()
        self.dispatch('on_edit')

    def on_build_form_pressed(self):
        """Handle build form button press"""
        if hasattr(self, 'menu') and self.menu:
            self.menu.dismiss()
        self.dispatch('on_build_form')

    def on_delete_pressed(self):
        """Handle delete button press"""
        if hasattr(self, 'menu') and self.menu:
            self.menu.dismiss()
        self.dispatch('on_delete')

    def _update_name(self, instance, value):
        """Update the name label"""
        if hasattr(self, 'ids') and self.ids.name_label:
            self.ids.name_label.text = value

    def _update_description(self, instance, value):
        """Update the description label"""
        if hasattr(self, 'ids') and self.ids.desc_label:
            self.ids.desc_label.text = value

    def _update_date(self, instance, value):
        """Update the date display"""
        try:
            if value:
                # Parse the date string
                if '.' in value:
                    date_str = value.split('.')[0]
                else:
                    date_str = value
                
                # Try different date formats
                date_formats = [
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d',
                    '%d/%m/%Y',
                    '%m/%d/%Y'
                ]
                
                parsed_date = None
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                
                if parsed_date:
                    # Update day and month labels
                    if hasattr(self, 'ids') and self.ids.day_label:
                        self.ids.day_label.text = str(parsed_date.day)
                    if hasattr(self, 'ids') and self.ids.month_label:
                        self.ids.month_label.text = parsed_date.strftime('%b').upper()
                else:
                    # Fallback for unparseable dates
                    if hasattr(self, 'ids') and self.ids.day_label:
                        self.ids.day_label.text = "??"
                    if hasattr(self, 'ids') and self.ids.month_label:
                        self.ids.month_label.text = "???"
            else:
                # No date provided
                if hasattr(self, 'ids') and self.ids.day_label:
                    self.ids.day_label.text = "--"
                if hasattr(self, 'ids') and self.ids.month_label:
                    self.ids.month_label.text = "---"
                    
        except Exception as e:
            print(f"Error updating date: {e}")
            if hasattr(self, 'ids') and self.ids.day_label:
                self.ids.day_label.text = "--"
            if hasattr(self, 'ids') and self.ids.month_label:
                self.ids.month_label.text = "---"

    def _update_sync_status(self, instance, value):
        """Update the sync status display"""
        if not hasattr(self, 'ids') or not self.ids.sync_status_label:
            return
            
        status = value.lower() if value else 'unknown'
        
        # Set status text and color
        if status == 'synced':
            self.ids.sync_status_label.text = "Synced"
            self.ids.sync_status_label.text_color = (0.2, 0.8, 0.2, 1)  # Green
        elif status == 'pending':
            self.ids.sync_status_label.text = "Pending"
            self.ids.sync_status_label.text_color = (1.0, 0.6, 0.0, 1)  # Orange
        elif status == 'failed':
            self.ids.sync_status_label.text = "Failed"
            self.ids.sync_status_label.text_color = (0.8, 0.2, 0.2, 1)  # Red
        else:
            self.ids.sync_status_label.text = "Unknown"
            self.ids.sync_status_label.text_color = (0.5, 0.5, 0.5, 1)  # Gray

    def on_edit(self, *args):
        """Default edit event handler"""
        pass

    def on_delete(self, *args):
        """Default delete event handler"""
        pass

    def on_build_form(self, *args):
        """Default build form event handler"""
        pass
