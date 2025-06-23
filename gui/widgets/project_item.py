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
        
        self.orientation = 'horizontal'
        self.padding = (dp(8), dp(8), dp(4), dp(8))
        self.spacing = dp(12)
        self.size_hint_y = None
        self.height = dp(72)
        self.elevation = 0.8
        
        # --- Date Circle ---
        date_circle = MDCard(
            size_hint=(None, None),
            size=(dp(56), dp(56)),
            radius=[dp(28)],
            md_bg_color=App.get_running_app().theme_cls.primary_light,
            ripple_behavior=False,
            elevation=0
        )
        date_circle.padding = dp(4)
        
        date_layout = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            padding=(0, dp(0)),
            spacing=dp(2),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.day_label = MDLabel(halign='center', font_style="H6", theme_text_color="Primary")
        self.month_label = MDLabel(halign='center', font_style="Caption", theme_text_color="Primary")
        date_layout.add_widget(self.day_label)
        date_layout.add_widget(self.month_label)
        date_circle.add_widget(date_layout)
        self.add_widget(date_circle)
        
        # --- Project Info ---
        info_layout = MDBoxLayout(orientation='vertical', adaptive_height=True, pos_hint={'center_y': 0.5})
        self.name_label = MDLabel(text=self.name, font_style="Subtitle1", adaptive_height=True)
        self.desc_label = MDLabel(text=self.description, font_style="Body2", theme_text_color="Secondary", adaptive_height=True)
        info_layout.add_widget(self.name_label)
        info_layout.add_widget(self.desc_label)
        self.add_widget(info_layout)

        # --- Right Aligned Items ---
        right_layout = MDBoxLayout(
            adaptive_width=True,
            spacing=dp(8),
            pos_hint={'center_y': 0.5}
        )

        # --- Sync Status Label ---
        self.sync_status_label = MDLabel(
            text="Unknown",
            font_style="Caption",
            halign="right",
            size_hint=(None, None),
            size=(dp(72), dp(24)),
            pos_hint={'center_y': 0.5},
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.5, 1)
        )
        right_layout.add_widget(self.sync_status_label)
        
        # --- Options Menu ---
        self.menu_button = MDIconButton(
            icon='dots-vertical',
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
