from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivymd.uix.card import MDCard
from kivy.metrics import dp
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.slider import MDSlider
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivy.core.window import Window
import datetime
import uuid
from kivymd.uix.snackbar import Snackbar

# Base response field class - only handles response input
class BaseResponseField(MDCard):
    """Base class for response-only fields used in data collection"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize responsive properties
        self.init_responsive_properties()
        
        # Bind to window resize for responsive updates
        Window.bind(on_resize=self._on_window_resize)
        
        # Clean card design with responsive spacing
        self.orientation = "vertical"
        self.update_responsive_layout()
        
        # Create the response input section
        self.create_response_input()
        
    def _on_window_resize(self, *args):
        """Handle window resize for responsive updates"""
        self.update_responsive_layout()
    
    def init_responsive_properties(self):
        """Initialize responsive properties based on screen size"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            self.responsive_helper = ResponsiveHelper
        except ImportError:
            self.responsive_helper = None
    
    def get_responsive_values(self):
        """Get responsive values based on screen size"""
        if not self.responsive_helper:
            # Fallback values for non-responsive mode
            return {
                'padding': dp(16),
                'spacing': dp(12),
                'button_height': dp(44),
                'input_height': dp(44),
                'font_size_main': "16sp",
                'font_size_secondary': "15sp",
                'font_size_small': "13sp"
            }
        
        category = self.responsive_helper.get_screen_size_category()
        
        # Responsive sizing based on device category
        if category == "large_tablet":
            return {
                'padding': dp(24),
                'spacing': dp(16),
                'button_height': dp(56),
                'input_height': dp(56),
                'font_size_main': "18sp",
                'font_size_secondary': "17sp",
                'font_size_small': "15sp"
            }
        elif category == "tablet":
            return {
                'padding': dp(20),
                'spacing': dp(14),
                'button_height': dp(52),
                'input_height': dp(52),
                'font_size_main': "17sp",
                'font_size_secondary': "16sp",
                'font_size_small': "14sp"
            }
        elif category == "small_tablet":
            return {
                'padding': dp(18),
                'spacing': dp(12),
                'button_height': dp(48),
                'input_height': dp(48),
                'font_size_main': "16sp",
                'font_size_secondary': "15sp",
                'font_size_small': "13sp"
            }
        else:  # phone
            return {
                'padding': dp(16),
                'spacing': dp(12),
                'button_height': dp(44),
                'input_height': dp(44),
                'font_size_main': "15sp",
                'font_size_secondary': "14sp",
                'font_size_small': "12sp"
            }
    
    def update_responsive_layout(self):
        """Update layout based on responsive values"""
        values = self.get_responsive_values()
        self.padding = values['padding']
        self.spacing = values['spacing']
        self.size_hint_y = None
        self.height = self.get_content_height()
        self.md_bg_color = (0.97, 0.97, 0.97, 1)  # Light gray background
        self.elevation = 0
        self.radius = [dp(6)]
        self.update_existing_widgets(values)
    
    def update_existing_widgets(self, values):
        """Update existing widgets with responsive values"""
        # Override in subclasses to update specific widgets
        pass
    
    def create_response_input(self):
        """Create the response input section - override in subclasses"""
        pass
    
    def get_value(self):
        """Get the current value - override in subclasses"""
        return None
    
    def set_value(self, value):
        """Set the current value - override in subclasses"""
        pass
    
    def get_content_height(self):
        """Get the content height - override in subclasses"""
        return dp(60)
    
    def validate(self):
        """Validate the input - override in subclasses"""
        return True

class TextResponseField(BaseResponseField):
    """Response field for text input"""
    
    def __init__(self, on_answer=None, **kwargs):
        self.hint_text = kwargs.pop('hint_text', 'Enter your answer')
        self.multiline = kwargs.pop('multiline', False)
        self.on_answer = on_answer
        super().__init__(**kwargs)
    
    def create_response_input(self):
        values = self.get_responsive_values()
        
        self.text_input = MDTextField(
            hint_text=self.hint_text,
            multiline=self.multiline,
            size_hint_y=None,
            height=values['input_height'],
            font_size=values['font_size_secondary'],
            mode="rectangle"
        )
        self.text_input.bind(text=self._on_text_change)
        self.add_widget(self.text_input)
    
    def update_existing_widgets(self, values):
        if hasattr(self, 'text_input'):
            self.text_input.height = values['input_height']
            self.text_input.font_size = values['font_size_secondary']
    
    def get_value(self):
        return self.text_input.text if hasattr(self, 'text_input') else ""
    
    def set_value(self, value):
        if hasattr(self, 'text_input'):
            self.text_input.text = str(value) if value else ""
    
    def get_content_height(self):
        if self.multiline:
            return dp(120)  # Taller for multiline
        return dp(80)

    def _on_text_change(self, instance, value):
        print(f"[DEBUG] TextResponseField value changed: {value}")
        if self.on_answer:
            self.on_answer()

class NumericResponseField(BaseResponseField):
    """Response field for numeric input"""
    
    def __init__(self, on_answer=None, **kwargs):
        self.hint_text = kwargs.pop('hint_text', 'Enter number')
        self.decimal = kwargs.pop('decimal', False)
        self.on_answer = on_answer
        super().__init__(**kwargs)
    
    def create_response_input(self):
        values = self.get_responsive_values()
        
        self.numeric_input = MDTextField(
            hint_text=self.hint_text,
            input_filter=None,  # We'll do our own filtering
            size_hint_y=None,
            height=values['input_height'],
            font_size=values['font_size_secondary'],
            mode="rectangle"
        )
        # Override insert_text for strict filtering
        if self.decimal:
            def insert_text_decimal(subself, substring, from_undo=False):
                s = subself.text
                allowed = '0123456789'
                # Only allow one decimal point
                if '.' in s:
                    substring = substring.replace('.', '')
                # Only allow minus at the start
                if '-' in s or subself.cursor_index() > 0:
                    substring = substring.replace('-', '')
                filtered = ''.join(c for c in substring if c in allowed or c == '.' or c == '-')
                return super(type(subself), subself).insert_text(filtered, from_undo=from_undo)
            self.numeric_input.insert_text = insert_text_decimal.__get__(self.numeric_input, MDTextField)
        else:
            def insert_text_int(subself, substring, from_undo=False):
                s = subself.text
                allowed = '0123456789'
                # Only allow minus at the start
                if '-' in s or subself.cursor_index() > 0:
                    substring = substring.replace('-', '')
                filtered = ''.join(c for c in substring if c in allowed or c == '-')
                return super(type(subself), subself).insert_text(filtered, from_undo=from_undo)
            self.numeric_input.insert_text = insert_text_int.__get__(self.numeric_input, MDTextField)
        self.numeric_input.bind(text=self._on_numeric_change)
        self.add_widget(self.numeric_input)
    
    def update_existing_widgets(self, values):
        if hasattr(self, 'numeric_input'):
            self.numeric_input.height = values['input_height']
            self.numeric_input.font_size = values['font_size_secondary']
    
    def get_value(self):
        if not hasattr(self, 'numeric_input'):
            return None
        
        text = self.numeric_input.text.strip()
        if not text:
            return None
        
        try:
            if self.decimal:
                return float(text)
            else:
                return int(text)
        except ValueError:
            return None
    
    def set_value(self, value):
        if hasattr(self, 'numeric_input'):
            self.numeric_input.text = str(value) if value is not None else ""
    
    def validate(self):
        value = self.get_value()
        if value is None and self.numeric_input.text.strip():
            return False
        return True
    
    def get_content_height(self):
        return dp(80)

    def _on_numeric_change(self, instance, value):
        print(f"[DEBUG] NumericResponseField value changed: {value}")
        valid = False
        if value.strip():
            try:
                if self.decimal:
                    float(value)
                else:
                    int(value)
                valid = True
            except ValueError:
                valid = False
        if not valid and value.strip():
            print("[DEBUG] Invalid numeric input! Clearing field.")
            instance.text = ""
            Snackbar(
                text="Please enter a valid number.",
                md_bg_color=(0, 0, 1, 1),
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=.5
            ).open()
        if self.on_answer:
            self.on_answer()

class ChoiceResponseField(BaseResponseField):
    """Response field for choice selection"""
    
    def __init__(self, options=None, allow_multiple=False, on_answer=None, **kwargs):
        self.options = options or []
        self.allow_multiple = allow_multiple
        self.selected_values = []
        self.on_answer = on_answer
        super().__init__(**kwargs)
    
    def create_response_input(self):
        values = self.get_responsive_values()
        
        # Create options container
        self.options_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None
        )
        
        # Create checkboxes and labels for each option
        self.checkboxes = []
        for i, option in enumerate(self.options):
            row = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(12),
                size_hint_y=None,
                height=values['button_height']
            )
            checkbox = MDCheckbox(
                size_hint=(None, None),
                size=(dp(32), dp(32)),
                pos_hint={'center_y': 0.5}
            )
            label = MDLabel(
                text=option,
                font_size=values['font_size_secondary'],
                theme_text_color="Primary",
                valign='middle'
            )
            checkbox.bind(active=self.on_option_selected)
            self.checkboxes.append(checkbox)
            row.add_widget(checkbox)
            row.add_widget(label)
            self.options_container.add_widget(row)
        
        self.add_widget(self.options_container)
    
    def update_existing_widgets(self, values):
        if hasattr(self, 'checkboxes'):
            for checkbox in self.checkboxes:
                checkbox.height = values['button_height']
                checkbox.font_size = values['font_size_secondary']
    
    def on_option_selected(self, instance, value):
        option_text = instance.text
        
        if self.allow_multiple:
            if value:
                if option_text not in self.selected_values:
                    self.selected_values.append(option_text)
            else:
                if option_text in self.selected_values:
                    self.selected_values.remove(option_text)
        else:
            # Single choice - uncheck others
            self.selected_values = [option_text] if value else []
            for checkbox in self.checkboxes:
                if checkbox != instance:
                    checkbox.active = False
        
        print(f"[DEBUG] ChoiceResponseField value changed: {self.selected_values}")
        if self.on_answer:
            self.on_answer()
    
    def get_value(self):
        if self.allow_multiple:
            return self.selected_values
        else:
            return self.selected_values[0] if self.selected_values else None
    
    def set_value(self, value):
        self.selected_values = []
        
        if self.allow_multiple and isinstance(value, list):
            self.selected_values = value
        elif not self.allow_multiple and value:
            self.selected_values = [value]
        
        # Update checkbox states
        for checkbox in self.checkboxes:
            checkbox.active = checkbox.text in self.selected_values
    
    def get_content_height(self):
        if not self.options:
            return dp(60)
        return len(self.options) * dp(48) + dp(20)

class ScaleResponseField(BaseResponseField):
    """Response field for rating scale"""
    
    def __init__(self, min_value=1, max_value=5, on_answer=None, **kwargs):
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = min_value
        self.on_answer = on_answer
        super().__init__(**kwargs)
    
    def create_response_input(self):
        values = self.get_responsive_values()
        
        # Create slider container
        slider_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None
        )
        
        # Value display
        self.value_label = MDLabel(
            text=str(self.current_value),
            halign='center',
            font_size=values['font_size_main'],
            bold=True
        )
        
        # Slider
        self.slider = MDSlider(
            min=self.min_value,
            max=self.max_value,
            value=self.current_value,
            size_hint_y=None,
            height=values['button_height']
        )
        self.slider.bind(value=self.on_slider_value)
        
        # Min/Max labels
        labels_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(16)
        )
        
        min_label = MDLabel(
            text=str(self.min_value),
            font_size=values['font_size_small'],
            theme_text_color="Secondary"
        )
        max_label = MDLabel(
            text=str(self.max_value),
            font_size=values['font_size_small'],
            theme_text_color="Secondary"
        )
        
        labels_container.add_widget(min_label)
        labels_container.add_widget(Widget())  # Spacer
        labels_container.add_widget(max_label)
        
        slider_container.add_widget(self.value_label)
        slider_container.add_widget(self.slider)
        slider_container.add_widget(labels_container)
        
        self.add_widget(slider_container)
    
    def update_existing_widgets(self, values):
        if hasattr(self, 'value_label'):
            self.value_label.font_size = values['font_size_main']
        if hasattr(self, 'slider'):
            self.slider.height = values['button_height']
    
    def on_slider_value(self, instance, value):
        self.current_value = int(value)
        if hasattr(self, 'value_label'):
            self.value_label.text = str(self.current_value)
        
        print(f"[DEBUG] ScaleResponseField value changed: {self.current_value}")
        if self.on_answer:
            self.on_answer()
    
    def get_value(self):
        return self.current_value
    
    def set_value(self, value):
        if value is not None:
            self.current_value = int(value)
            if hasattr(self, 'slider'):
                self.slider.value = self.current_value
            if hasattr(self, 'value_label'):
                self.value_label.text = str(self.current_value)
    
    def get_content_height(self):
        return dp(120)

class DateResponseField(BaseResponseField):
    """Response field for date selection"""
    
    def __init__(self, on_answer=None, **kwargs):
        self.on_answer = on_answer
        self.selected_date = None
        super().__init__(**kwargs)
    
    def create_response_input(self):
        values = self.get_responsive_values()
        
        # Date display and picker button
        date_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(12),
            size_hint_y=None,
            height=values['button_height']
        )
        
        self.date_label = MDLabel(
            text="Select date",
            font_size=values['font_size_secondary'],
            theme_text_color="Secondary"
        )
        
        self.date_button = MDRaisedButton(
            text="Choose Date",
            size_hint_y=None,
            height=values['button_height'],
            font_size=values['font_size_secondary']
        )
        self.date_button.bind(on_release=self.show_date_picker)
        
        date_container.add_widget(self.date_label)
        date_container.add_widget(self.date_button)
        
        self.add_widget(date_container)
    
    def update_existing_widgets(self, values):
        if hasattr(self, 'date_label'):
            self.date_label.font_size = values['font_size_secondary']
        if hasattr(self, 'date_button'):
            self.date_button.height = values['button_height']
            self.date_button.font_size = values['font_size_secondary']
    
    def show_date_picker(self, instance):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.set_date)
        date_dialog.open()
    
    def set_date(self, instance, date_obj, *args):
        self.selected_date = date_obj
        if hasattr(self, 'date_label'):
            self.date_label.text = date_obj.strftime("%Y-%m-%d")
            self.date_label.theme_text_color = "Primary"
        if self.on_answer:
            self.on_answer()
    
    def get_value(self):
        return self.selected_date.isoformat() if self.selected_date else None
    
    def set_value(self, value):
        if value:
            try:
                if isinstance(value, str):
                    self.selected_date = datetime.datetime.fromisoformat(value).date()
                else:
                    self.selected_date = value
                
                if hasattr(self, 'date_label'):
                    self.date_label.text = self.selected_date.strftime("%Y-%m-%d")
                    self.date_label.theme_text_color = "Primary"
            except Exception as e:
                print(f"Error setting date value: {e}")
    
    def get_content_height(self):
        return dp(80)

class DateTimeResponseField(BaseResponseField):
    """Response field for date and time selection"""
    
    def __init__(self, on_answer=None, **kwargs):
        self.on_answer = on_answer
        self.selected_datetime = None
        super().__init__(**kwargs)
    
    def create_response_input(self):
        values = self.get_responsive_values()
        
        # Date and time container
        datetime_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None
        )
        
        # Date section
        date_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(12),
            size_hint_y=None,
            height=values['button_height']
        )
        
        self.date_label = MDLabel(
            text="Select date",
            font_size=values['font_size_secondary'],
            theme_text_color="Secondary"
        )
        
        self.date_button = MDRaisedButton(
            text="Date",
            size_hint_y=None,
            height=values['button_height'],
            font_size=values['font_size_secondary']
        )
        self.date_button.bind(on_release=self.show_date_picker)
        
        date_container.add_widget(self.date_label)
        date_container.add_widget(self.date_button)
        
        # Time section
        time_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(12),
            size_hint_y=None,
            height=values['button_height']
        )
        
        self.time_label = MDLabel(
            text="Select time",
            font_size=values['font_size_secondary'],
            theme_text_color="Secondary"
        )
        
        self.time_button = MDRaisedButton(
            text="Time",
            size_hint_y=None,
            height=values['button_height'],
            font_size=values['font_size_secondary']
        )
        self.time_button.bind(on_release=self.show_time_picker)
        
        time_container.add_widget(self.time_label)
        time_container.add_widget(self.time_button)
        
        datetime_container.add_widget(date_container)
        datetime_container.add_widget(time_container)
        
        self.add_widget(datetime_container)
    
    def update_existing_widgets(self, values):
        if hasattr(self, 'date_label'):
            self.date_label.font_size = values['font_size_secondary']
        if hasattr(self, 'date_button'):
            self.date_button.height = values['button_height']
            self.date_button.font_size = values['font_size_secondary']
        if hasattr(self, 'time_label'):
            self.time_label.font_size = values['font_size_secondary']
        if hasattr(self, 'time_button'):
            self.time_button.height = values['button_height']
            self.time_button.font_size = values['font_size_secondary']
    
    def show_date_picker(self, instance):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.set_date)
        date_dialog.open()
    
    def show_time_picker(self, instance):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.set_time)
        time_dialog.open()
    
    def set_date(self, instance, date_obj, *args):
        if self.selected_datetime:
            time = self.selected_datetime.time()
            self.selected_datetime = datetime.datetime.combine(date_obj, time)
        else:
            self.selected_datetime = datetime.datetime.combine(date_obj, datetime.time(0, 0))
        
        if hasattr(self, 'date_label'):
            self.date_label.text = date_obj.strftime("%Y-%m-%d")
            self.date_label.theme_text_color = "Primary"
        if self.on_answer:
            self.on_answer()
    
    def set_time(self, instance, time_obj):
        if self.selected_datetime:
            date = self.selected_datetime.date()
            self.selected_datetime = datetime.datetime.combine(date, time_obj)
        else:
            today = datetime.date.today()
            self.selected_datetime = datetime.datetime.combine(today, time_obj)
        
        if hasattr(self, 'time_label'):
            self.time_label.text = time_obj.strftime("%H:%M")
            self.time_label.theme_text_color = "Primary"
        if self.on_answer:
            self.on_answer()
    
    def get_value(self):
        return self.selected_datetime.isoformat() if self.selected_datetime else None
    
    def set_value(self, value):
        if value:
            try:
                if isinstance(value, str):
                    self.selected_datetime = datetime.datetime.fromisoformat(value)
                else:
                    self.selected_datetime = value
                
                if hasattr(self, 'date_label') and self.selected_datetime:
                    self.date_label.text = self.selected_datetime.strftime("%Y-%m-%d")
                    self.date_label.theme_text_color = "Primary"
                
                if hasattr(self, 'time_label') and self.selected_datetime:
                    self.time_label.text = self.selected_datetime.strftime("%H:%M")
                    self.time_label.theme_text_color = "Primary"
            except Exception as e:
                print(f"Error setting datetime value: {e}")
    
    def get_content_height(self):
        return dp(120)

class FileResponseField(BaseResponseField):
    """Response field for file upload"""
    
    def __init__(self, on_answer=None, **kwargs):
        self.selected_file = None
        self.on_answer = on_answer
        super().__init__(**kwargs)
    
    def create_response_input(self):
        values = self.get_responsive_values()
        
        # File selection container
        file_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None
        )
        
        # File info display
        self.file_label = MDLabel(
            text="No file selected",
            font_size=values['font_size_secondary'],
            theme_text_color="Secondary"
        )
        
        # Buttons container
        buttons_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=values['button_height']
        )
        
        self.choose_button = MDRaisedButton(
            text="Choose File",
            size_hint_y=None,
            height=values['button_height'],
            font_size=values['font_size_secondary']
        )
        self.choose_button.bind(on_release=self.choose_file)
        
        self.clear_button = MDRaisedButton(
            text="Clear",
            size_hint_y=None,
            height=values['button_height'],
            font_size=values['font_size_secondary']
        )
        self.clear_button.bind(on_release=self.clear_file)
        
        buttons_container.add_widget(self.choose_button)
        buttons_container.add_widget(self.clear_button)
        
        file_container.add_widget(self.file_label)
        file_container.add_widget(buttons_container)
        
        self.add_widget(file_container)
    
    def update_existing_widgets(self, values):
        if hasattr(self, 'file_label'):
            self.file_label.font_size = values['font_size_secondary']
        if hasattr(self, 'choose_button'):
            self.choose_button.height = values['button_height']
            self.choose_button.font_size = values['font_size_secondary']
        if hasattr(self, 'clear_button'):
            self.clear_button.height = values['button_height']
            self.clear_button.font_size = values['font_size_secondary']
    
    def choose_file(self, instance):
        print("File chooser would open here")
        self.selected_file = f"sample_file_{uuid.uuid4().hex[:8]}.txt"
        if hasattr(self, 'file_label'):
            self.file_label.text = f"Selected: {self.selected_file}"
            self.file_label.theme_text_color = "Primary"
        
        print(f"[DEBUG] FileResponseField value changed: {self.selected_file}")
        if self.on_answer:
            self.on_answer()
    
    def clear_file(self, instance):
        self.selected_file = None
        if hasattr(self, 'file_label'):
            self.file_label.text = "No file selected"
            self.file_label.theme_text_color = "Secondary"
        
        print(f"[DEBUG] FileResponseField value changed: {self.selected_file}")
        if self.on_answer:
            self.on_answer()
    
    def get_value(self):
        return self.selected_file
    
    def set_value(self, value):
        self.selected_file = value
        if hasattr(self, 'file_label'):
            if value:
                self.file_label.text = f"Selected: {value}"
                self.file_label.theme_text_color = "Primary"
            else:
                self.file_label.text = "No file selected"
                self.file_label.theme_text_color = "Secondary"
    
    def get_content_height(self):
        return dp(100)

# Factory function to create response fields
def create_response_field(response_type, **kwargs):
    """Create a response field based on the response type"""
    
    # Remove hint_text, multiline, and on_answer from kwargs if present to avoid multiple values error
    hint_text = kwargs.pop('hint_text', None)
    multiline = kwargs.pop('multiline', None)
    on_answer = kwargs.pop('on_answer', None)
    
    if response_type in ['text', 'long_text']:
        return TextResponseField(
            multiline=(response_type == 'long_text') if multiline is None else multiline,
            hint_text=('Enter your answer' if response_type == 'text' else 'Enter detailed answer') if hint_text is None else hint_text,
            on_answer=on_answer,
            **kwargs
        )
    elif response_type in ['numeric', 'numeric_integer']:
        return NumericResponseField(
            decimal=False,
            hint_text='Enter whole number',
            on_answer=on_answer,
            **kwargs
        )
    elif response_type in ['numeric_decimal']:
        return NumericResponseField(
            decimal=True,
            hint_text='Enter decimal number',
            on_answer=on_answer,
            **kwargs
        )
    elif response_type in ['choice', 'choice_single']:
        options = kwargs.pop('options', [])
        return ChoiceResponseField(
            options=options,
            allow_multiple=False,
            on_answer=on_answer,
            **kwargs
        )
    elif response_type in ['choice_multiple']:
        options = kwargs.pop('options', [])
        return ChoiceResponseField(
            options=options,
            allow_multiple=True,
            on_answer=on_answer,
            **kwargs
        )
    elif response_type == 'scale':
        return ScaleResponseField(
            min_value=kwargs.get('min_value', 1),
            max_value=kwargs.get('max_value', 5),
            on_answer=on_answer,
            **kwargs
        )
    elif response_type == 'date':
        return DateResponseField(on_answer=on_answer, **kwargs)
    elif response_type == 'datetime':
        return DateTimeResponseField(on_answer=on_answer, **kwargs)
    elif response_type == 'file':
        return FileResponseField(on_answer=on_answer, **kwargs)
    else:
        # Default to text field for unknown types
        return TextResponseField(hint_text='Enter your answer', on_answer=on_answer, **kwargs) 