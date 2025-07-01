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

class ProjectItem(MDCard, EventDispatcher):
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
        
        # Get responsive sizing
        self.setup_responsive_layout()
        
        # --- Date Circle ---
        date_circle = MDCard(
            size_hint=(None, None),
            size=self.get_date_circle_size(),
            radius=[self.get_date_circle_radius()],
            md_bg_color=App.get_running_app().theme_cls.primary_light,
            ripple_behavior=False,
            elevation=0
        )
        date_circle.padding = self.get_date_circle_padding()
        
        date_layout = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            padding=(0, dp(0)),
            spacing=self.get_date_layout_spacing(),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.day_label = MDLabel(
            halign='center', 
            font_style="H6" if not self.is_tablet() else "H5",  # Larger font for tablets
            theme_text_color="Primary"
        )
        self.month_label = MDLabel(
            halign='center', 
            font_style="Caption" if not self.is_tablet() else "Body2",  # Larger font for tablets
            theme_text_color="Primary"
        )
        date_layout.add_widget(self.day_label)
        date_layout.add_widget(self.month_label)
        date_circle.add_widget(date_layout)
        self.add_widget(date_circle)
        
        # --- Project Info ---
        info_layout = MDBoxLayout(
            orientation='vertical', 
            adaptive_height=True, 
            pos_hint={'center_y': 0.5},
            spacing=self.get_info_layout_spacing()
        )
        self.name_label = MDLabel(
            text=self.name, 
            font_style="Subtitle1" if not self.is_tablet() else "H6",  # Larger font for tablets
            adaptive_height=True,
            font_size=self.get_name_font_size()
        )
        self.desc_label = MDLabel(
            text=self.description, 
            font_style="Body2" if not self.is_tablet() else "Body1",  # Larger font for tablets
            theme_text_color="Secondary", 
            adaptive_height=True,
            font_size=self.get_description_font_size()
        )
        info_layout.add_widget(self.name_label)
        info_layout.add_widget(self.desc_label)
        self.add_widget(info_layout)

        # --- Right Aligned Items ---
        right_layout = MDBoxLayout(
            adaptive_width=True,
            spacing=self.get_right_layout_spacing(),
            pos_hint={'center_y': 0.5}
        )

        # --- Sync Status Label ---
        self.sync_status_label = MDLabel(
            text="Unknown",
            font_style="Caption" if not self.is_tablet() else "Body2",
            halign="right",
            size_hint=(None, None),
            size=self.get_sync_status_size(),
            pos_hint={'center_y': 0.5},
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.5, 1),
            font_size=self.get_sync_status_font_size()
        )
        right_layout.add_widget(self.sync_status_label)
        
        # --- Options Menu ---
        self.menu_button = MDIconButton(
            icon='dots-vertical',
            size_hint=(None, None),
            size=self.get_menu_button_size(),
            user_font_size=self.get_menu_icon_size(),
            on_release=self.open_menu,
            pos_hint={'center_y': 0.5}
        )
        right_layout.add_widget(self.menu_button)
        self.add_widget(right_layout)

        menu_items = [
            {"text": "Edit", "viewclass": "OneLineListItem", "on_release": lambda: self.dispatch('on_edit')},
            {"text": "Build Form", "viewclass": "OneLineListItem", "on_release": lambda: self.dispatch('on_build_form')},
            {"text": "Delete", "viewclass": "OneLineListItem", "on_release": lambda: self.dispatch('on_delete')},
        ]
        self.menu = MDDropdownMenu(
            caller=self.menu_button,
            items=menu_items,
            width_mult=4,
        )

        self.bind(name=self._update_name)
        self.bind(description=self._update_description)
        self.bind(created_at=self._update_date)
        self.bind(sync_status=self._update_sync_status)

        # Populate initial data
        self._update_date(self, self.created_at)
        self._update_sync_status(self, self.sync_status)

    def setup_responsive_layout(self):
        """Setup responsive layout properties"""
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
        self.menu.open()

    def _update_name(self, instance, value):
        self.name_label.text = value
    
    def _update_description(self, instance, value):
        self.desc_label.text = value
    
    def _update_date(self, instance, value):
        if not value:
            self.day_label.text = "--"
            self.month_label.text = "N/A"
            return
            
        try:
            if '.' in value:
                dt_object = datetime.fromisoformat(value.split('.')[0])
            else:
                dt_object = datetime.fromisoformat(value.replace('Z', ''))
            
            self.day_label.text = dt_object.strftime("%d")
            self.month_label.text = dt_object.strftime("%b").upper()
        except (ValueError, TypeError):
            self.day_label.text = "!"
            self.month_label.text = "Err"

    def _update_sync_status(self, instance, value):
        status_map = {
            'synced': ('Synced', (0.0, 0.6, 0.2, 1)),   # Green
            'pending': ('Pending', (0.9, 0.6, 0, 1)),   # Amber
            'failed': ('Failed', (0.8, 0, 0, 1)),       # Red
            'unknown': ('Unknown', (0.5, 0.5, 0.5, 1))  # Grey
        }

        label_text, color = status_map.get(value.lower(), status_map['unknown'])

        self.sync_status_label.text = label_text
        self.sync_status_label.theme_text_color = 'Custom'
        self.sync_status_label.text_color = color

    def on_edit(self, *args):
        self.menu.dismiss()
    
    def on_delete(self, *args):
        self.menu.dismiss()

    def on_build_form(self, *args):
        self.menu.dismiss()
