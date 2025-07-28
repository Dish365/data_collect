"""
Response Fields Module for Data Collection - KivyMD 2.0.1
Creates different types of response widgets for form questions
Fully responsive and follows Material Design 3 principles
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivymd.uix.card import MDCard
from kivy.metrics import dp
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.slider import MDSlider
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivy.core.window import Window
import datetime
import uuid
from utils.cross_platform_toast import toast
from widgets.responsive_layout import ResponsiveHelper


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
        Clock.schedule_once(lambda dt: self.update_responsive_layout(), 0.1)
    
    def init_responsive_properties(self):
        """Initialize responsive properties based on screen size"""
        try:
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
                'font_size_small': "13sp",
                'touch_target': dp(44)
            }
        
        category = self.responsive_helper.get_screen_size_category()
        
        # Responsive sizing based on device category
        if category == ResponsiveHelper.LARGE_TABLET:
            return {
                'padding': dp(24),
                'spacing': dp(16),
                'button_height': dp(56),
                'input_height': dp(56),
                'font_size_main': "18sp",
                'font_size_secondary': "17sp",
                'font_size_small': "15sp",
                'touch_target': dp(56)
            }
        elif category == ResponsiveHelper.TABLET:
            return {
                'padding': dp(20),
                'spacing': dp(14),
                'button_height': dp(52),
                'input_height': dp(52),
                'font_size_main': "17sp",
                'font_size_secondary': "16sp",
                'font_size_small': "14sp",
                'touch_target': dp(52)
            }
        elif category == ResponsiveHelper.SMALL_TABLET:
            return {
                'padding': dp(18),
                'spacing': dp(12),
                'button_height': dp(48),
                'input_height': dp(48),
                'font_size_main': "16sp",
                'font_size_secondary': "15sp",
                'font_size_small': "13sp",
                'touch_target': dp(48)
            }
        else:  # phone
            return {
                'padding': dp(16),
                'spacing': dp(12),
                'button_height': dp(44),
                'input_height': dp(44),
                'font_size_main': "15sp",
                'font_size_secondary': "14sp",
                'font_size_small': "12sp",
                'touch_target': dp(44)
            }
    
    def update_responsive_layout(self):
        """Update layout based on responsive values"""
        values = self.get_responsive_values()
        self.padding = values['padding']
        self.spacing = values['spacing']
        self.size_hint_y = None
        self.height = self.get_content_height()
        self.md_bg_color = self.theme_cls.surface_variant if hasattr(self, 'theme_cls') else [0.97, 0.97, 0.97, 1]
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
        self.input_filter = kwargs.pop('input_filter', None)
        self.on_answer = on_answer
        super().__init__(**kwargs)
    
    def create_response_input(self):
        values = self.get_responsive_values()
        
        # Create text field with modern KivyMD 2.0.1 structure
        self.text_input = MDTextField(
            mode="outlined",
            multiline=self.multiline,
            input_filter=self.input_filter,
            size_hint_y=None,
            height=values['input_height'] * (2 if self.multiline else 1),
            font_size=values['font_size_secondary']
        )
        
        # Add hint text as child component
        hint_text_widget = MDTextFieldHintText(text=self.hint_text)
        self.text_input.add_widget(hint_text_widget)
        
        self.text_input.bind(text=self._on_text_change)
        self.add_widget(self.text_input)
    
    def update_existing_widgets(self, values):
        if hasattr(self, 'text_input'):
            self.text_input.height = values['input_height'] * (2 if self.multiline else 1)
            self.text_input.font_size = values['font_size_secondary']
    
    def get_value(self):
        return self.text_input.text if hasattr(self, 'text_input') else ""
    
    def set_value(self, value):
        if hasattr(self, 'text_input'):
            self.text_input.text = str(value) if value else ""
    
    def get_content_height(self):
        values = self.get_responsive_values()
        base_height = values['input_height'] * (2 if self.multiline else 1) + values['padding'] * 2
        return max(base_height, dp(80))

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
        
        # Create numeric input field
        self.numeric_input = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=values['input_height'],
            font_size=values['font_size_secondary']
        )
        
        # Add hint text as child component
        hint_text_widget = MDTextFieldHintText(text=self.hint_text)
        self.numeric_input.add_widget(hint_text_widget)
        
        # Override insert_text for strict numeric filtering
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
        values = self.get_responsive_values()
        return values['input_height'] + values['padding'] * 2

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
            Clock.schedule_once(lambda dt: setattr(instance, 'text', ''), 0.1)
            toast("Please enter a valid number.")
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
            # Create option row
            row = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(12),
                size_hint_y=None,
                height=values['touch_target'],
                padding=[dp(8), 0]
            )
            
            # Checkbox
            checkbox = MDCheckbox(
                size_hint=(None, None),
                size=(dp(28), dp(28)),
                pos_hint={'center_y': 0.5}
            )
            
            # Store the option text with the checkbox for easy access
            checkbox.option_text = option
            checkbox.bind(active=self.on_option_selected)
            self.checkboxes.append(checkbox)
            
            # Label
            label = MDLabel(
                text=option,
                font_size=values['font_size_secondary'],
                theme_text_color="Primary",
                valign='middle',
                text_size=(None, None)
            )
            
            row.add_widget(checkbox)
            row.add_widget(label)
            self.options_container.add_widget(row)
        
        # Update container height
        self.options_container.height = len(self.options) * (values['touch_target'] + dp(8))
        self.add_widget(self.options_container)
    
    def update_existing_widgets(self, values):
        if hasattr(self, 'checkboxes'):
            for i, checkbox in enumerate(self.checkboxes):
                # Update checkbox parent row height
                if checkbox.parent:
                    checkbox.parent.height = values['touch_target']
        
        if hasattr(self, 'options_container'):
            self.options_container.height = len(self.options) * (values['touch_target'] + dp(8))
    
    def on_option_selected(self, instance, value):
        option_text = instance.option_text
        
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
            checkbox.active = checkbox.option_text in self.selected_values
    
    def get_content_height(self):
        if not self.options:
            return dp(60)
        values = self.get_responsive_values()
        return len(self.options) * (values['touch_target'] + dp(8)) + values['padding'] * 2


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
            bold=True,
            size_hint_y=None,
            height=dp(32)
        )
        
        # Scale labels container
        labels_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(20)
        )
        
        # Create labels for each scale point
        for i in range(self.min_value, self.max_value + 1):
            label = MDLabel(
                text=str(i),
                halign='center',
                font_size=values['font_size_small'],
                theme_text_color="Secondary"
            )
            labels_container.add_widget(label)
        
        # Slider
        self.slider = MDSlider(
            min=self.min_value,
            max=self.max_value,
            value=self.current_value,
            step=1,
            size_hint_y=None,
            height=values['touch_target'],
            hint=False,
            color=self.theme_cls.primary_color if hasattr(self, 'theme_cls') else [0.2, 0.6, 1, 1]
        )
        self.slider.bind(value=self.on_slider_value)
        
        slider_container.add_widget(self.value_label)
        slider_container.add_widget(labels_container)
        slider_container.add_widget(self.slider)
        
        # Update container height
        slider_container.height = dp(32) + dp(20) + values['touch_target'] + dp(16)  # spacing
        self.add_widget(slider_container)
    
    def update_existing_widgets(self, values):
        if hasattr(self, 'value_label'):
            self.value_label.font_size = values['font_size_main']
        if hasattr(self, 'slider'):
            self.slider.height = values['touch_target']
    
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
        values = self.get_responsive_values()
        return dp(32) + dp(20) + values['touch_target'] + dp(16) + values['padding'] * 2


class DateResponseField(BaseResponseField):
    """Response field for date selection"""
    
    def __init__(self, on_answer=None, **kwargs):
        self.on_answer = on_answer
        self.selected_date = None
        super().__init__(**kwargs)
    
    def create_response_input(self):
        values = self.get_responsive_values()
        
        # Date display and picker container
        date_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(12),
            size_hint_y=None,
            height=values['button_height']
        )
        
        # Date display label
        self.date_label = MDLabel(
            text="No date selected",
            font_size=values['font_size_secondary'],
            theme_text_color="Secondary",
            valign='middle'
        )
        
        # Date picker button using KivyMD 2.0.1 structure
        self.date_button = MDButton(
            style="elevated",
            size_hint=(None, None),
            size=(dp(120), values['button_height'])
        )
        
        # Add button text as child component
        button_text = MDButtonText(text="Choose Date")
        self.date_button.add_widget(button_text)
        self.date_button.bind(on_release=self.show_date_picker)
        
        date_container.add_widget(self.date_label)
        date_container.add_widget(self.date_button)
        self.add_widget(date_container)
    
    def update_existing_widgets(self, values):
        if hasattr(self, 'date_label'):
            self.date_label.font_size = values['font_size_secondary']
        if hasattr(self, 'date_button'):
            self.date_button.size = (dp(120), values['button_height'])
    
    def show_date_picker(self, instance):
        """Show date picker - placeholder implementation"""
        # Note: In a real implementation, you would use MDDatePicker
        # For now, we'll simulate date selection
        import datetime
        today = datetime.date.today()
        self.set_date_value(today)
    
    def set_date_value(self, date_obj):
        """Set the selected date"""
        self.selected_date = date_obj
        if hasattr(self, 'date_label'):
            self.date_label.text = date_obj.strftime("%Y-%m-%d")
            self.date_label.theme_text_color = "Primary"
        
        print(f"[DEBUG] DateResponseField value changed: {date_obj}")
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
        values = self.get_responsive_values()
        return values['button_height'] + values['padding'] * 2


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
            text="No date selected",
            font_size=values['font_size_secondary'],
            theme_text_color="Secondary",
            valign='middle'
        )
        
        self.date_button = MDButton(
            style="elevated",
            size_hint=(None, None),
            size=(dp(100), values['button_height'])
        )
        date_button_text = MDButtonText(text="Date")
        self.date_button.add_widget(date_button_text)
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
            text="No time selected",
            font_size=values['font_size_secondary'],
            theme_text_color="Secondary",
            valign='middle'
        )
        
        self.time_button = MDButton(
            style="elevated",
            size_hint=(None, None),
            size=(dp(100), values['button_height'])
        )
        time_button_text = MDButtonText(text="Time")
        self.time_button.add_widget(time_button_text)
        self.time_button.bind(on_release=self.show_time_picker)
        
        time_container.add_widget(self.time_label)
        time_container.add_widget(self.time_button)
        
        datetime_container.add_widget(date_container)
        datetime_container.add_widget(time_container)
        
        # Update container height
        datetime_container.height = values['button_height'] * 2 + dp(8)
        self.add_widget(datetime_container)
    
    def update_existing_widgets(self, values):
        if hasattr(self, 'date_label'):
            self.date_label.font_size = values['font_size_secondary']
        if hasattr(self, 'date_button'):
            self.date_button.size = (dp(100), values['button_height'])
        if hasattr(self, 'time_label'):
            self.time_label.font_size = values['font_size_secondary']
        if hasattr(self, 'time_button'):
            self.time_button.size = (dp(100), values['button_height'])
    
    def show_date_picker(self, instance):
        """Show date picker - placeholder implementation"""
        import datetime
        today = datetime.date.today()
        self.set_date_value(today)
    
    def show_time_picker(self, instance):
        """Show time picker - placeholder implementation"""
        import datetime
        current_time = datetime.time(12, 0)  # Default to noon
        self.set_time_value(current_time)
    
    def set_date_value(self, date_obj):
        """Set the selected date"""
        if self.selected_datetime:
            time = self.selected_datetime.time()
            self.selected_datetime = datetime.datetime.combine(date_obj, time)
        else:
            self.selected_datetime = datetime.datetime.combine(date_obj, datetime.time(0, 0))
        
        if hasattr(self, 'date_label'):
            self.date_label.text = date_obj.strftime("%Y-%m-%d")
            self.date_label.theme_text_color = "Primary"
        
        print(f"[DEBUG] DateTimeResponseField date changed: {self.selected_datetime}")
        if self.on_answer:
            self.on_answer()
    
    def set_time_value(self, time_obj):
        """Set the selected time"""
        if self.selected_datetime:
            date = self.selected_datetime.date()
            self.selected_datetime = datetime.datetime.combine(date, time_obj)
        else:
            today = datetime.date.today()
            self.selected_datetime = datetime.datetime.combine(today, time_obj)
        
        if hasattr(self, 'time_label'):
            self.time_label.text = time_obj.strftime("%H:%M")
            self.time_label.theme_text_color = "Primary"
        
        print(f"[DEBUG] DateTimeResponseField time changed: {self.selected_datetime}")
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
        values = self.get_responsive_values()
        return values['button_height'] * 2 + dp(8) + values['padding'] * 2


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
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(24)
        )
        
        # Buttons container
        buttons_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=values['button_height']
        )
        
        # Choose file button
        self.choose_button = MDButton(
            style="elevated",
            size_hint_x=0.7,
            size_hint_y=None,
            height=values['button_height']
        )
        choose_button_text = MDButtonText(text="Choose File")
        self.choose_button.add_widget(choose_button_text)
        self.choose_button.bind(on_release=self.choose_file)
        
        # Clear button
        self.clear_button = MDButton(
            style="outlined",
            size_hint_x=0.3,
            size_hint_y=None,
            height=values['button_height']
        )
        clear_button_text = MDButtonText(text="Clear")
        self.clear_button.add_widget(clear_button_text)
        self.clear_button.bind(on_release=self.clear_file)
        
        buttons_container.add_widget(self.choose_button)
        buttons_container.add_widget(self.clear_button)
        
        file_container.add_widget(self.file_label)
        file_container.add_widget(buttons_container)
        
        # Update container height
        file_container.height = dp(24) + values['button_height'] + dp(8)
        self.add_widget(file_container)
    
    def update_existing_widgets(self, values):
        if hasattr(self, 'file_label'):
            self.file_label.font_size = values['font_size_secondary']
        if hasattr(self, 'choose_button'):
            self.choose_button.height = values['button_height']
        if hasattr(self, 'clear_button'):
            self.clear_button.height = values['button_height']
    
    def choose_file(self, instance):
        """Simulate file selection - in real implementation would open file chooser"""
        print("File chooser would open here")
        self.selected_file = f"sample_file_{uuid.uuid4().hex[:8]}.txt"
        if hasattr(self, 'file_label'):
            self.file_label.text = f"Selected: {self.selected_file}"
            self.file_label.theme_text_color = "Primary"
        
        print(f"[DEBUG] FileResponseField value changed: {self.selected_file}")
        if self.on_answer:
            self.on_answer()
    
    def clear_file(self, instance):
        """Clear file selection"""
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
        values = self.get_responsive_values()
        return dp(24) + values['button_height'] + dp(8) + values['padding'] * 2


def create_response_field(response_type, **kwargs):
    """
    Factory function to create response fields for KivyMD 2.0.1
    
    Args:
        response_type: Type of field ('text', 'choice_single', 'choice_multiple', 'scale', 'date', 'file')
        **kwargs: Additional arguments specific to field type
    
    Returns:
        Appropriate response field instance
    """
    
    # Extract common parameters
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
            hint_text='Enter whole number' if hint_text is None else hint_text,
            on_answer=on_answer,
            **kwargs
        )
    elif response_type in ['numeric_decimal']:
        return NumericResponseField(
            decimal=True,
            hint_text='Enter decimal number' if hint_text is None else hint_text,
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
            min_value=kwargs.pop('min_value', 1),
            max_value=kwargs.pop('max_value', 5),
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
        return TextResponseField(
            hint_text='Enter your answer' if hint_text is None else hint_text, 
            on_answer=on_answer, 
            **kwargs
        )


def get_field_placeholder(field_type):
    """Get appropriate placeholder text for field type"""
    placeholders = {
        'text': "Enter your answer",
        'long_text': "Enter your detailed answer",
        'numeric': "Enter a number",
        'numeric_integer': "Enter a whole number",
        'numeric_decimal': "Enter a decimal number",
        'date': "Select a date",
        'datetime': "Select date and time",
        'location': "Enter location",
        'choice': "Select an option",
        'choice_single': "Select an option",
        'choice_multiple': "Select options",
        'scale': "Rate on scale",
        'file': "Choose a file"
    }
    return placeholders.get(field_type, "Enter your answer")


def validate_response_field(field_type, value):
    """Validate response field value based on type"""
    if not value:
        return True, ""  # Empty is valid for most fields
    
    if field_type in ['numeric', 'numeric_integer']:
        try:
            int(value)
            return True, ""
        except (ValueError, TypeError):
            return False, "Please enter a valid whole number"
    
    elif field_type == 'numeric_decimal':
        try:
            float(value)
            return True, ""
        except (ValueError, TypeError):
            return False, "Please enter a valid number"
    
    elif field_type == 'date':
        try:
            if isinstance(value, str):
                datetime.datetime.fromisoformat(value)
            return True, ""
        except ValueError:
            return False, "Please select a valid date"
    
    elif field_type == 'datetime':
        try:
            if isinstance(value, str):
                datetime.datetime.fromisoformat(value)
            return True, ""
        except ValueError:
            return False, "Please select a valid date and time"
    
    return True, ""