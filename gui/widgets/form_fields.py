from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.boxlayout import BoxLayout 
from kivy.metrics import dp
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.slider import MDSlider
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.toast import toast
from kivy.clock import Clock
from kivy.core.window import Window
import datetime
import uuid

# Base field class for all form fields
class BaseFormField(MDCard):
    question_text = StringProperty("")
    response_type = StringProperty("text_short")
    question_number = StringProperty("1")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize responsive properties
        self.init_responsive_properties()
        
        # Bind to window resize for responsive updates
        Window.bind(on_resize=self._on_window_resize)
        
        # Clean card design with responsive spacing
        self.orientation = "vertical"
        self.update_responsive_layout()
        
        # Header section with question number and type
        self.create_header_section()
        
        # Question text section with clean styling
        self.create_question_section()
        
        # Response section with visual separator  
        self.create_response_section()
        
        # Bind properties for updates
        self.bind(question_text=self.on_question_text_change)
        self.bind(question_number=self.on_question_number_change)
    
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
                'height': dp(240),
                'padding': dp(24),
                'spacing': dp(16),
                'button_height': dp(48),
                'input_height': dp(48),
                'header_height': dp(40),
                'font_size_main': "18sp",
                'font_size_secondary': "16sp",
                'font_size_small': "14sp"
            }
        
        category = self.responsive_helper.get_screen_size_category()
        
        # Responsive sizing based on device category
        if category == "large_tablet":
            return {
                'height': dp(300),
                'padding': dp(32),
                'spacing': dp(24),
                'button_height': dp(56),
                'input_height': dp(56),
                'header_height': dp(48),
                'font_size_main': "20sp",
                'font_size_secondary': "18sp",
                'font_size_small': "16sp"
            }
        elif category == "tablet":
            return {
                'height': dp(260),
                'padding': dp(28),
                'spacing': dp(20),
                'button_height': dp(52),
                'input_height': dp(52),
                'header_height': dp(44),
                'font_size_main': "19sp",
                'font_size_secondary': "17sp",
                'font_size_small': "15sp"
            }
        elif category == "small_tablet":
            return {
                'height': dp(240),
                'padding': dp(24),
                'spacing': dp(18),
                'button_height': dp(48),
                'input_height': dp(48),
                'header_height': dp(40),
                'font_size_main': "18sp",
                'font_size_secondary': "16sp",
                'font_size_small': "14sp"
            }
        else:  # phone
            return {
                'height': dp(220),
                'padding': dp(20),
                'spacing': dp(16),
                'button_height': dp(44),
                'input_height': dp(44),
                'header_height': dp(36),
                'font_size_main': "16sp",
                'font_size_secondary': "15sp",
                'font_size_small': "13sp"
            }
    
    def update_responsive_layout(self):
        values = self.get_responsive_values()
        # Reduce top padding to dp(8), keep left/right/bottom as before
        self.padding = [values['padding'], dp(8), values['padding'], values['padding']]
        self.spacing = values['spacing']
        self.size_hint_y = None
        self.height = values['height'] + self.get_content_height() + dp(8)
        self.md_bg_color = (1, 1, 1, 1)
        self.elevation = 0.6
        self.update_existing_widgets(values)
    
    def update_existing_widgets(self, values):
        """Update existing widgets with responsive values"""
        # Update header components
        if hasattr(self, 'header_card'):
            self.header_card.height = values['header_height']
        
        if hasattr(self, 'question_number_label'):
            self.question_number_label.font_size = values['font_size_main']
        
        if hasattr(self, 'response_type_label'):
            self.response_type_label.font_size = values['font_size_small']
        
        # Update question input
        if hasattr(self, 'question_input'):
            self.question_input.height = values['input_height']
            self.question_input.font_size = values['font_size_secondary']
        
        # Update labels
        if hasattr(self, 'question_label'):
            self.question_label.font_size = values['font_size_secondary']
        
        if hasattr(self, 'response_label'):
            self.response_label.font_size = values['font_size_secondary']
    
    def create_header_section(self):
        values = self.get_responsive_values()
        # Remove any extra top padding in header
        self.header_card = MDCard(
            orientation='horizontal',
            size_hint_y=None,
            height=values['header_height'],
            padding=[values['padding'] * 0.6, 0, values['padding'] * 0.6, 0],  # No top/bottom padding
            spacing=dp(12),
            md_bg_color=(0.95, 0.95, 0.95, 1),
            elevation=0
        )
        self.question_number_label = MDLabel(
            text=f"Question {self.question_number}",
            font_style="Subtitle1",
            theme_text_color="Primary",
            bold=True,
            size_hint_x=None,
            width=dp(120),
            font_size=values['font_size_main']
        )
        self.response_type_label = MDLabel(
            text=self.get_response_type_display(),
            font_style="Caption",
            theme_text_color="Secondary",
            halign="right",
            font_size=values['font_size_small']
        )
        self.header_card.add_widget(self.question_number_label)
        self.header_card.add_widget(self.response_type_label)
        self.add_widget(self.header_card)
    
    def create_question_section(self):
        """Create responsive question section"""
        values = self.get_responsive_values()
        
        question_section = MDBoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(80 + (values['input_height'] - 44))  # Adjust for larger inputs
        )
        
        self.question_label = MDLabel(
            text="Question Text",
            font_style="Body1",
            theme_text_color="Primary",
            bold=True,
            size_hint_y=None,
            height=dp(28),
            font_size=values['font_size_secondary']
        )
        question_section.add_widget(self.question_label)
        
        # Responsive text input with larger touch targets
        self.question_input = MDTextField(
            text=self.question_text,
            hint_text="Enter your question here...",
            mode="rectangle",
            multiline=False,
            size_hint_y=None,
            height=values['input_height'],
            font_size=values['font_size_secondary']
        )
        question_section.add_widget(self.question_input)
        self.add_widget(question_section)
    
    def create_response_section(self):
        """Create responsive response section"""
        values = self.get_responsive_values()
        
        response_section = MDBoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(36)
        )
        
        # Visual separator line
        separator = MDBoxLayout(
            size_hint_y=None,
            height=dp(1),
            md_bg_color=(0.9, 0.9, 0.9, 1)
        )
        response_section.add_widget(separator)
        
        self.response_label = MDLabel(
            text="Response Input",
            font_style="Body1",
            theme_text_color="Secondary",
            bold=True,
            size_hint_y=None,
            height=dp(28),
            font_size=values['font_size_secondary']
        )
        response_section.add_widget(self.response_label)
        self.add_widget(response_section)
        
    def get_response_type_display(self):
        """Get display name for response type"""
        type_display = {
            'text_short': 'Short Text',
            'text_long': 'Long Text',
            'numeric_integer': 'Number (Integer)',
            'numeric_decimal': 'Number (Decimal)',
            'choice_single': 'Single Choice',
            'choice_multiple': 'Multiple Choice',
            'scale_rating': 'Rating Scale',
            'date': 'Date',
            'datetime': 'Date & Time',
            'geopoint': 'GPS Location',
            'image': 'Photo/Image',
            'audio': 'Audio Recording',
            'barcode': 'Barcode/QR Code',
        }
        return type_display.get(self.response_type, self.response_type)
        
    def on_question_text_change(self, instance, value):
        """Update the question input field when question_text property changes"""
        if hasattr(self, 'question_input'):
            self.question_input.text = value
    
    def on_question_number_change(self, instance, value):
        """Update the question number label when question_number property changes"""
        if hasattr(self, 'question_number_label'):
            self.question_number_label.text = f"Question {value}"
        
    def get_question_text(self):
        """Get the current question text from the input field"""
        return self.question_input.text.strip() if hasattr(self, 'question_input') else ""
        
    def get_value(self):
        """Override in subclasses to return the field value"""
        return ""
    
    def set_value(self, value):
        """Override in subclasses to set the field value"""
        pass
    
    def validate(self):
        """Override in subclasses to validate the field"""
        errors = []
        
        # Validate question text
        question_text = self.get_question_text()
        if not question_text:
            errors.append("Question text is required")
        elif len(question_text) < 3:
            errors.append("Question text must be at least 3 characters long")
        elif question_text.lower().startswith("new "):
            errors.append("Please enter a meaningful question (remove 'New' prefix)")
            
        return len(errors) == 0, errors

    def get_content_height(self):
        """Override in subclasses to return extra content height."""
        return 0

    def update_field_height(self):
        values = self.get_responsive_values()
        extra_padding = dp(24)
        self.height = values['height'] + self.get_content_height() + extra_padding

    def create_delete_button(self):
        values = self.get_responsive_values()
        self.delete_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=values['button_height'],
            spacing=dp(10)
        )
        spacer = MDBoxLayout(size_hint_x=1)
        self.delete_container.add_widget(spacer)
        self.delete_button = MDRaisedButton(
            text="Delete Question",
            md_bg_color=(1, 0.3, 0.3, 1),
            on_release=lambda x: self.parent.remove_widget(self),
            size_hint=(None, None),
            size=(dp(140), values['button_height']),
            font_size=values['font_size_small']
        )
        self.delete_container.add_widget(self.delete_button)
        self.add_widget(self.delete_container)

class ShortTextField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "text_short"
        self.create_text_input()
        self.create_delete_button()
        self.update_field_height()
    
    def create_text_input(self):
        """Create responsive text input field"""
        values = self.get_responsive_values()
        
        self.text_input = MDTextField(
            hint_text="Short text answer",
            mode="rectangle",
            size_hint_y=None,
            height=values['input_height'],
            font_size=values['font_size_secondary']
        )
        self.add_widget(self.text_input)
    
    def _on_window_resize(self, *args):
        """Handle window resize"""
        super()._on_window_resize(*args)
        if hasattr(self, 'text_input'):
            values = self.get_responsive_values()
            self.text_input.height = values['input_height']
            self.text_input.font_size = values['font_size_secondary']

    def get_value(self):
        return self.text_input.text.strip() if hasattr(self, 'text_input') else ""

    def set_value(self, value):
        if hasattr(self, 'text_input'):
            self.text_input.text = str(value)

    def get_content_height(self):
        values = self.get_responsive_values()
        return values['input_height'] + values['input_height'] 

class LongTextField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "text_long"
        self.create_text_input()
        self.create_delete_button()
        self.update_field_height()
    
    def create_text_input(self):
        """Create responsive multiline text input field"""
        values = self.get_responsive_values()
        
        # Larger height for long text on tablets
        long_text_height = values['input_height'] * 2.5  # 2.5x taller for long text
        
        self.text_input = MDTextField(
            hint_text="Long text answer (multiple lines)",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=long_text_height,
            font_size=values['font_size_secondary']
        )
        self.add_widget(self.text_input)
        
        # Adjust card height for long text field
        self.height = values['height'] + (long_text_height - values['input_height'])
    
    def _on_window_resize(self, *args):
        """Handle window resize"""
        super()._on_window_resize(*args)
        if hasattr(self, 'text_input'):
            values = self.get_responsive_values()
            long_text_height = values['input_height'] * 2.5
            self.text_input.height = long_text_height
            self.text_input.font_size = values['font_size_secondary']
            self.height = values['height'] + (long_text_height - values['input_height'])

    def get_value(self):
        return self.text_input.text.strip() if hasattr(self, 'text_input') else ""

    def set_value(self, value):
        if hasattr(self, 'text_input'):
            self.text_input.text = str(value)

    def get_content_height(self):
        values = self.get_responsive_values()
        long_text_height = values['input_height'] * 2.5
        return long_text_height + values['input_height'] - dp(16)

class NumericIntegerField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "numeric_integer"
        self.create_numeric_input()
        self.create_delete_button()
        self.update_field_height()
    
    def create_numeric_input(self):
        """Create responsive numeric input field"""
        values = self.get_responsive_values()
        
        self.number_input = MDTextField(
            hint_text="Enter a whole number",
            input_filter="int",  # Only allow integers
            mode="rectangle",
            size_hint_y=None,
            height=values['input_height'],
            font_size=values['font_size_secondary']
        )
        self.add_widget(self.number_input)
    
    def _on_window_resize(self, *args):
        """Handle window resize"""
        super()._on_window_resize(*args)
        if hasattr(self, 'number_input'):
            values = self.get_responsive_values()
            self.number_input.height = values['input_height']
            self.number_input.font_size = values['font_size_secondary']

    def get_value(self):
        try:
            value = self.number_input.text.strip()
            return int(value) if value else None
        except (ValueError, AttributeError):
            return None

    def set_value(self, value):
        if hasattr(self, 'number_input'):
            self.number_input.text = str(value) if value is not None else ""

    def validate(self):
        is_valid, errors = super().validate()
        value = self.get_value()
        if self.number_input.text.strip() and value is None:
            errors.append("Please enter a valid whole number")
            is_valid = False
        return is_valid, errors

    def get_content_height(self):
        values = self.get_responsive_values()
        return values['input_height'] + values['input_height'] + dp(8)

class NumericDecimalField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "numeric_decimal"
        self.create_decimal_input()
        self.create_delete_button()
        self.update_field_height()
    
    def create_decimal_input(self):
        """Create responsive decimal input field"""
        values = self.get_responsive_values()
        
        self.number_input = MDTextField(
            hint_text="Enter a decimal number",
            input_filter="float",  # Allow decimal numbers
            mode="rectangle",
            size_hint_y=None,
            height=values['input_height'],
            font_size=values['font_size_secondary']
        )
        self.add_widget(self.number_input)
    
    def _on_window_resize(self, *args):
        """Handle window resize"""
        super()._on_window_resize(*args)
        if hasattr(self, 'number_input'):
            values = self.get_responsive_values()
            self.number_input.height = values['input_height']
            self.number_input.font_size = values['font_size_secondary']

    def get_value(self):
        try:
            value = self.number_input.text.strip()
            return float(value) if value else None
        except (ValueError, AttributeError):
            return None

    def set_value(self, value):
        if hasattr(self, 'number_input'):
            self.number_input.text = str(value) if value is not None else ""

    def validate(self):
        is_valid, errors = super().validate()
        value = self.get_value()
        if self.number_input.text.strip() and value is None:
            errors.append("Please enter a valid decimal number")
            is_valid = False
        return is_valid, errors

    def get_content_height(self):
        values = self.get_responsive_values()
        return values['input_height'] + values['input_height'] + dp(8)

class SingleChoiceField(BaseFormField):
    options = ListProperty([])

    def __init__(self, question_text="", options=None, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "choice_single"
        self.selected_option = None
        self.checkboxes = []
        self.create_options_header()
        self.create_options_container()
        self.options = options if options else ['Option 1', 'Option 2']
        self.create_delete_button()
        self.update_field_height()

    def create_options_header(self):
        self.options_header = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(40)
        )
        self.options_label = MDLabel(
            text="Options:",
            size_hint_x=0.4,
            font_style="Subtitle2",
            theme_text_color="Primary",
            font_size="14sp",
            halign="left",
            valign="middle"
        )
        self.add_option_btn = MDRaisedButton(
            text="Add Option",
            size_hint_x=None,
            width=dp(90),
            height=dp(32),
            font_size="12sp",
            on_release=self.add_option
        )
        self.remove_option_btn = MDRaisedButton(
            text="Remove Last",
            size_hint_x=None,
            width=dp(110),
            height=dp(32),
            font_size="12sp",
            on_release=self.remove_last_option
        )
        self.options_header.add_widget(self.options_label)
        self.options_header.add_widget(self.add_option_btn)
        self.options_header.add_widget(self.remove_option_btn)
        self.add_widget(self.options_header)

    def create_options_container(self):
        self.options_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
            adaptive_height=True
        )
        self.add_widget(self.options_container)

    def on_options(self, instance, options):
        print(f"SingleChoiceField.on_options called with: {options}")
        # Store current user-entered text from existing option inputs
        current_texts = {}
        if hasattr(self, 'option_inputs'):
            for i, input_widget in enumerate(self.option_inputs):
                if i < len(self.options):
                    current_texts[i] = input_widget.text
        
        self.options_container.clear_widgets()
        self.checkboxes = []
        self.option_inputs = []  # Store references to option input widgets
        if not options:
            print("No options provided, returning early")
            return
        values = self.get_responsive_values()
        option_row_height = values['input_height'] + dp(8)
        for i, option in enumerate(options):
            row = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(8),
                size_hint_y=None,
                height=option_row_height
            )
            checkbox = MDCheckbox(
                size_hint=(None, None),
                size=(dp(20), dp(20)),
                pos_hint={'center_y': 0.5},
                on_active=lambda x, active, opt=option: self.on_option_selected(opt, active)
            )
            
            # Use user-entered text if available, otherwise use the option text
            display_text = current_texts.get(i, option)
            option_input = MDTextField(
                text=display_text,
                size_hint_x=0.8,
                font_size="13sp",
                height=values['input_height'],
                size_hint_y=None,
                mode="rectangle",
                pos_hint={'center_y': 0.5},
                on_text_validate=lambda instance, idx=i: self.update_option(idx, instance.text)
            )
            option_input.bind(on_text_validate=lambda instance, idx=i: self.update_option(idx, instance.text))
            row.add_widget(checkbox)
            row.add_widget(option_input)
            self.options_container.add_widget(row)
            self.checkboxes.append(checkbox)
            self.option_inputs.append(option_input)
        self.update_field_height()

    def add_option(self, instance):
        """Add a new option to the choice field"""
        new_option = f"Option {len(self.options) + 1}"
        self.options = self.options + [new_option]
        toast("Option added. You can edit the option text directly.")
        self.update_field_height()
    
    def remove_last_option(self, instance):
        """Remove the last option from the choice field"""
        if len(self.options) > 2:  # Keep at least 2 options
            self.options = self.options[:-1]
            toast("Option removed.")
        else:
            toast("Single choice questions need at least 2 options.")
        self.update_field_height()
    
    def on_option_selected(self, option, active):
        if active:
            self.selected_option = option
    
    def update_option(self, index, new_text):
        """Update an option text"""
        if 0 <= index < len(self.options) and new_text.strip():
            # Only update if the text actually changed
            if self.options[index] != new_text.strip():
                options_list = list(self.options)
                options_list[index] = new_text.strip()
                self.options = options_list
    
    def get_value(self):
        return self.selected_option
    
    def set_value(self, value):
        self.selected_option = value
        # Update UI to reflect the selection
        for i, option in enumerate(self.options):
            if option == value and i < len(self.checkboxes):
                self.checkboxes[i].active = True
    
    def validate(self):
        is_valid, errors = super().validate()
        if len(self.options) < 2:
            errors.append("Single choice questions need at least 2 options")
            is_valid = False
        
        # Check for empty options
        empty_options = [i for i, opt in enumerate(self.options) if not opt.strip()]
        if empty_options:
            errors.append("Please fill in all option texts")
            is_valid = False
            
        return is_valid, errors

    def get_content_height(self):
        values = self.get_responsive_values()
        base = values['input_height'] + values['input_height']
        options_header_height = self.options_header.height if hasattr(self, 'options_header') else dp(40)
        option_row_height = values['input_height'] + dp(8)
        total_option_height = len(self.options) * option_row_height
        return base + options_header_height + total_option_height

class MultipleChoiceField(BaseFormField):
    options = ListProperty([])

    def __init__(self, question_text="", options=None, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "choice_multiple"
        self.selected_options = []
        self.checkboxes = []
        self.create_options_header()
        self.create_options_container()
        self.options = options if options else ['Option 1', 'Option 2']
        self.create_delete_button()
        self.update_field_height()

    def create_options_header(self):
        self.options_header = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(40)
        )
        self.options_label = MDLabel(
            text="Options:",
            size_hint_x=0.4,
            font_style="Subtitle2",
            theme_text_color="Primary",
            font_size="14sp",
            halign="left",
            valign="middle"
        )
        self.add_option_btn = MDRaisedButton(
            text="Add Option",
            size_hint_x=None,
            width=dp(90),
            height=dp(32),
            font_size="12sp",
            on_release=self.add_option
        )
        self.remove_option_btn = MDRaisedButton(
            text="Remove Last",
            size_hint_x=None,
            width=dp(110),
            height=dp(32),
            font_size="12sp",
            on_release=self.remove_last_option
        )
        self.options_header.add_widget(self.options_label)
        self.options_header.add_widget(self.add_option_btn)
        self.options_header.add_widget(self.remove_option_btn)
        self.add_widget(self.options_header)

    def create_options_container(self):
        self.options_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
            adaptive_height=True
        )
        self.add_widget(self.options_container)

    def on_options(self, instance, options):
        print(f"MultipleChoiceField.on_options called with: {options}")
        # Store current user-entered text from existing option inputs
        current_texts = {}
        if hasattr(self, 'option_inputs'):
            for i, input_widget in enumerate(self.option_inputs):
                if i < len(self.options):
                    current_texts[i] = input_widget.text
        
        self.options_container.clear_widgets()
        self.checkboxes = []
        self.option_inputs = []  # Store references to option input widgets
        values = self.get_responsive_values()
        option_row_height = values['input_height'] + dp(8)
        for i, option in enumerate(options):
            row = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(8),
                size_hint_y=None,
                height=option_row_height
            )
            checkbox = MDCheckbox(
                size_hint=(None, None),
                size=(dp(20), dp(20)),
                pos_hint={'center_y': 0.5},
                on_active=lambda x, active, opt=option: self.on_option_selected(opt, active)
            )
            
            # Use user-entered text if available, otherwise use the option text
            display_text = current_texts.get(i, option)
            option_input = MDTextField(
                text=display_text,
                size_hint_x=0.8,
                font_size="13sp",
                height=values['input_height'],
                size_hint_y=None,
                mode="rectangle",
                pos_hint={'center_y': 0.5},
                on_text_validate=lambda instance, idx=i: self.update_option(idx, instance.text)
            )
            option_input.bind(on_text_validate=lambda instance, idx=i: self.update_option(idx, instance.text))
            row.add_widget(checkbox)
            row.add_widget(option_input)
            self.options_container.add_widget(row)
            self.checkboxes.append(checkbox)
            self.option_inputs.append(option_input)
        self.update_field_height()

    def add_option(self, instance):
        """Add a new option to the choice field"""
        new_option = f"Option {len(self.options) + 1}"
        self.options = self.options + [new_option]
        toast("Option added. You can edit the option text directly.")
        self.update_field_height()

    def remove_last_option(self, instance):
        """Remove the last option from the choice field"""
        if len(self.options) > 2:
            self.options = self.options[:-1]
            toast("Option removed.")
        else:
            toast("Multiple choice questions need at least 2 options.")
        self.update_field_height()

    def update_option(self, index, new_text):
        """Update an option text"""
        if 0 <= index < len(self.options) and new_text.strip():
            # Only update if the text actually changed
            if self.options[index] != new_text.strip():
                options_list = list(self.options)
                options_list[index] = new_text.strip()
                self.options = options_list
    
    def on_option_selected(self, option, active):
        if active and option not in self.selected_options:
            self.selected_options.append(option)
        elif not active and option in self.selected_options:
            self.selected_options.remove(option)
    
    def get_value(self):
        return self.selected_options
    
    def set_value(self, value):
        self.selected_options = value if isinstance(value, list) else []
        # Update UI to reflect the selections
        for i, option in enumerate(self.options):
            if option in self.selected_options and i < len(self.checkboxes):
                self.checkboxes[i].active = True
    
    def validate(self):
        is_valid, errors = super().validate()
        if len(self.options) < 2:
            errors.append("Multiple choice questions need at least 2 options")
            is_valid = False
        
        # Check for empty options
        empty_options = [i for i, opt in enumerate(self.options) if not opt.strip()]
        if empty_options:
            errors.append("Please fill in all option texts")
            is_valid = False
            
        return is_valid, errors

    def get_content_height(self):
        values = self.get_responsive_values()
        base = values['input_height'] + values['input_height']
        options_header_height = self.options_header.height if hasattr(self, 'options_header') else dp(40)
        option_row_height = values['input_height'] + dp(8)
        total_option_height = len(self.options) * option_row_height
        return base + options_header_height + total_option_height

class RatingScaleField(BaseFormField):
    min_value = NumericProperty(1)
    max_value = NumericProperty(5)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "scale_rating"
        self.current_value = self.min_value
        self.value_label = MDLabel(
            text=f"Rating: {self.current_value}",
            theme_text_color="Secondary",
            font_style="Body1",
            size_hint_y=None,
            height=dp(30)
        )
        self.slider = MDSlider(
            min=self.min_value,
            max=self.max_value,
            value=self.min_value,
            step=1,
            size_hint_y=None,
            height=dp(30)
        )
        self.slider.bind(value=self.on_slider_value)
        self.add_widget(self.value_label)
        self.add_widget(self.slider)
        self.create_delete_button()
        self.update_field_height()

    def get_content_height(self):
        values = self.get_responsive_values()
        return values['input_height'] + values['input_height'] + dp(8) + dp(30) + dp(30) + dp(2)

    def on_slider_value(self, instance, value):
        self.current_value = int(value)
        self.value_label.text = f"Rating: {self.current_value}"
    
    def get_value(self):
        return self.current_value
    
    def set_value(self, value):
        if value is not None:
            self.current_value = int(value)
            self.slider.value = self.current_value
            self.value_label.text = f"Rating: {self.current_value}"

    def get_content_height(self):
        return dp(60)  # 2x 30dp for label and slider

class DateField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "date"
        self.selected_date = None
        self.create_date_input()
        self.create_delete_button()
        self.update_field_height()

    def create_date_input(self):
        values = self.get_responsive_values()
        self.date_input = MDTextField(
            hint_text="Select date",
            mode="rectangle",
            size_hint_y=None,
            height=values['input_height'],
            font_size=values['font_size_secondary'],
            readonly=True,
            on_focus=self.show_date_picker
        )
        self.add_widget(self.date_input)

    def show_date_picker(self, instance, focus):
        if focus:
            date_dialog = MDDatePicker()
            date_dialog.bind(on_save=self.set_date)
            date_dialog.open()
    
    def set_date(self, instance, date_obj, *_):
        self.selected_date = date_obj
        self.date_input.text = date_obj.strftime('%Y-%m-%d')
        instance.dismiss()
    
    def get_value(self):
        return self.selected_date.strftime('%Y-%m-%d') if self.selected_date else None
    
    def set_value(self, value):
        if value:
            try:
                self.selected_date = datetime.datetime.strptime(value, '%Y-%m-%d').date()
                self.date_input.text = value
            except ValueError:
                pass

    def get_content_height(self):
        values = self.get_responsive_values()
        return values['input_height'] + values['input_height'] + dp(8) + values['input_height'] + dp(2)

class DateTimeField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "datetime"
        self.selected_date = None
        self.selected_time = None
        self.create_datetime_inputs()
        self.create_delete_button()
        self.update_field_height()

    def create_datetime_inputs(self):
        values = self.get_responsive_values()
        self.date_input = MDTextField(
            hint_text="Select date",
            mode="rectangle",
            size_hint_y=None,
            height=values['input_height'],
            font_size=values['font_size_secondary'],
            readonly=True,
            on_focus=self.show_date_picker
        )
        self.time_input = MDTextField(
            hint_text="Select time",
            mode="rectangle",
            size_hint_y=None,
            height=values['input_height'],
            font_size=values['font_size_secondary'],
            readonly=True,
            on_focus=self.show_time_picker
        )
        self.add_widget(self.date_input)
        self.add_widget(self.time_input)

    def show_date_picker(self, instance, focus):
        if focus:
            date_dialog = MDDatePicker()
            date_dialog.bind(on_save=self.set_date)
            date_dialog.open()
    
    def show_time_picker(self, instance, focus):
        if focus:
            time_dialog = MDTimePicker()
            time_dialog.bind(on_save=self.set_time)
            time_dialog.open()

    def set_date(self, instance, date_obj, *_):
        self.selected_date = date_obj
        self.date_input.text = date_obj.strftime('%Y-%m-%d')
        instance.dismiss()
    
    def set_time(self, instance, time_obj, *_):
        self.selected_time = time_obj
        self.time_input.text = time_obj.strftime('%H:%M')
        instance.dismiss()
    
    def get_value(self):
        if self.selected_date and self.selected_time:
            dt = datetime.datetime.combine(self.selected_date, self.selected_time)
            return dt.strftime('%Y-%m-%d %H:%M')
        return None
    
    def set_value(self, value):
        if value:
            try:
                dt = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M')
                self.selected_date = dt.date()
                self.selected_time = dt.time()
                self.date_input.text = dt.strftime('%Y-%m-%d')
                self.time_input.text = dt.strftime('%H:%M')
            except ValueError:
                pass

    def get_content_height(self):
        values = self.get_responsive_values()
        return values['input_height'] + values['input_height'] + dp(8) + values['input_height'] + values['input_height'] + dp(2)

class LocationPickerField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "geopoint"
        self.current_location = None
        self.gps_accuracy = None
        self.is_getting_location = False
        self.create_location_input()
        self.create_delete_button()
        self.update_field_height()

    def create_location_input(self):
        values = self.get_responsive_values()
        
        # Location display field
        self.location_input = MDTextField(
            hint_text="No location captured",
            mode="rectangle",
            size_hint_y=None,
            height=values['input_height'],
            font_size=values['font_size_secondary'],
            readonly=True
        )
        
        # GPS buttons
        self.button_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=values['button_height']
        )
        
        self.get_location_btn = MDRaisedButton(
            text="Get GPS Location",
            size_hint_x=0.7,
            on_release=self.get_current_location
        )
        
        self.clear_location_btn = MDRaisedButton(
            text="Clear",
            size_hint_x=0.3,
            on_release=self.clear_location
        )
        
        self.button_container.add_widget(self.get_location_btn)
        self.button_container.add_widget(self.clear_location_btn)
        
        # GPS status/accuracy info
        self.gps_info_label = MDLabel(
            text="",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20),
            font_size="12sp"
        )
        
        self.add_widget(self.location_input)
        self.add_widget(self.button_container)
        self.add_widget(self.gps_info_label)

    def get_current_location(self, instance):
        """Get current GPS location"""
        if self.is_getting_location:
            return
            
        self.is_getting_location = True
        self.get_location_btn.text = "Getting Location..."
        self.get_location_btn.disabled = True
        toast("Getting GPS location...")
        
        # Simulate GPS acquisition delay and then get location
        Clock.schedule_once(self._simulate_gps_result, 2)
    
    def _simulate_gps_result(self, dt):
        """Simulate GPS result - in real app would use plyer.gps"""
        import random
        
        # Simulate realistic GPS coordinates (example: around Montreal, Canada)
        base_lat = 45.5017  # Montreal latitude
        base_lon = -73.5673  # Montreal longitude
        
        # Add small random offset to simulate movement
        lat_offset = random.uniform(-0.01, 0.01)  # ~1km range
        lon_offset = random.uniform(-0.01, 0.01)  # ~1km range
        
        lat = round(base_lat + lat_offset, 6)
        lon = round(base_lon + lon_offset, 6)
        
        # Simulate GPS accuracy (typical smartphone GPS accuracy)
        accuracy = round(random.uniform(3.0, 15.0), 1)  # 3-15 meters
        
        self.current_location = {
            'latitude': lat, 
            'longitude': lon,
            'accuracy': accuracy,
            'timestamp': datetime.datetime.now().isoformat(),
            'provider': 'gps'
        }
        self.gps_accuracy = accuracy
        
        # Update display
        self.location_input.text = f"Lat: {lat}, Lon: {lon}"
        self.gps_info_label.text = f"Accuracy: ±{accuracy}m | Captured: {datetime.datetime.now().strftime('%H:%M:%S')}"
        
        # Reset button
        self.get_location_btn.text = "Get GPS Location"
        self.get_location_btn.disabled = False
        self.is_getting_location = False
        
        toast(f"Location captured with {accuracy}m accuracy!")
    
    def clear_location(self, instance):
        """Clear captured location"""
        self.current_location = None
        self.gps_accuracy = None
        self.location_input.text = ""
        self.location_input.hint_text = "No location captured"
        self.gps_info_label.text = ""
        toast("Location cleared")
    
    def get_value(self):
        """Return the GPS location with metadata"""
        return self.current_location
    
    def set_value(self, value):
        """Set location value from saved data"""
        if value and isinstance(value, dict):
            self.current_location = value
            lat = value.get('latitude', 0)
            lon = value.get('longitude', 0)
            accuracy = value.get('accuracy')
            timestamp = value.get('timestamp', '')
            
            self.location_input.text = f"Lat: {lat}, Lon: {lon}"
            
            if accuracy and timestamp:
                time_str = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp
                self.gps_info_label.text = f"Accuracy: ±{accuracy}m | Captured: {time_str}"

    def get_content_height(self):
        values = self.get_responsive_values()
        return values['input_height'] + values['button_height'] + dp(20) + dp(16)

class PhotoUploadField(BaseFormField):
    def __init__(self, **kwargs):
        self.photo_path = None  # Ensure attribute exists before any parent or Kivy code runs
        super().__init__(**kwargs)
        self.response_type = "image"
        self.update_field_height()

    def create_response_section(self):
        # Only add the photo controls as the response section, below the question label
        self.create_photo_input()

    def create_photo_input(self):
        """Create enhanced photo input interface with preview"""
        values = self.get_responsive_values()
        
        # Photo display area
        self.photo_display = MDTextField(
            hint_text="No photo selected",
            mode="rectangle",
            readonly=True,
            size_hint_y=None,
            height=values['input_height'],
            font_size=values['font_size_secondary']
        )
        
        # Photo preview area (hidden initially)
        self.photo_preview = MDCard(
            size_hint_y=None,
            height=dp(120),
            md_bg_color=(0.95, 0.95, 0.95, 1),
            elevation=1,
            opacity=0  # Hidden initially
        )
        
        self.preview_label = MDLabel(
            text="Photo Preview",
            halign="center",
            valign="center",
            theme_text_color="Secondary",
            font_size="14sp"
        )
        self.photo_preview.add_widget(self.preview_label)
        
        # Button container with three buttons
        self.button_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=values['button_height']
        )
        
        self.camera_btn = MDRaisedButton(
            text="📷 Camera",
            size_hint_x=0.33,
            on_release=self.take_photo,
            font_size=values['font_size_small']
        )
        
        self.gallery_btn = MDRaisedButton(
            text="🖼️ Gallery",
            size_hint_x=0.33,
            on_release=self.choose_from_gallery,
            font_size=values['font_size_small']
        )
        
        self.clear_btn = MDRaisedButton(
            text="🗑️ Clear",
            size_hint_x=0.33,
            on_release=self.clear_photo,
            md_bg_color=(0.8, 0.2, 0.2, 1),
            font_size=values['font_size_small']
        )
        
        self.button_container.add_widget(self.camera_btn)
        self.button_container.add_widget(self.gallery_btn)
        self.button_container.add_widget(self.clear_btn)
        
        self.add_widget(self.photo_display)
        self.add_widget(self.photo_preview)
        self.add_widget(self.button_container)

    def take_photo(self, instance):
        """Take a photo using the device camera"""
        try:
            from plyer import camera
            
            def on_camera_result(filename):
                if filename:
                    # Handle the captured photo
                    self.photo_path = filename
                    self.photo_display.text = f"Photo: {filename.split('/')[-1]}"
                    self._update_photo_preview(filename)
                    toast("Photo captured successfully!")
                else:
                    toast("Photo capture cancelled")
            
            # Take photo with camera
            camera.take_picture(
                filename=f"photo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                on_complete=on_camera_result
            )
            
        except ImportError:
            # Fallback for when plyer is not available
            self.photo_path = f"photo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            self.photo_display.text = f"Photo: {self.photo_path}"
            toast("Photo captured! (Simulated)")
        except Exception as e:
            toast(f"Camera error: {str(e)}")
    
    def choose_from_gallery(self, instance):
        """Choose a photo from the device gallery"""
        try:
            from plyer import filechooser
            
            def on_file_result(selection):
                if selection:
                    # Handle the selected file
                    file_path = selection[0]  # First selected file
                    
                    # Validate file type
                    allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
                    file_ext = file_path.lower()[file_path.rfind('.'):]
                    
                    if file_ext in allowed_extensions:
                        self.photo_path = file_path
                        self.photo_display.text = f"Photo: {file_path.split('/')[-1]}"
                        self._update_photo_preview(file_path)
                        toast("Photo selected successfully!")
                    else:
                        toast("Please select a valid image file (JPG, PNG, BMP, GIF, TIFF)")
                else:
                    toast("No file selected")
            
            # Open file chooser for images
            filechooser.open_file(
                title="Select Photo",
                filters=[("Image files", "*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif", "*.tiff")],
                on_selection=on_file_result
            )
            
        except ImportError:
            # Fallback for when plyer is not available
            self.photo_path = f"gallery_photo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            self.photo_display.text = f"Photo: {self.photo_path}"
            toast("Photo selected! (Simulated)")
        except Exception as e:
            toast(f"File chooser error: {str(e)}")
    
    def clear_photo(self, instance):
        """Clear the selected photo"""
        self.photo_path = None
        self.photo_display.text = ""
        self.photo_display.hint_text = "No photo selected"
        
        # Hide preview
        self.photo_preview.opacity = 0
        self.preview_label.text = "Photo Preview"
        
        toast("Photo cleared")
    
    def _update_photo_preview(self, file_path):
        """Update the photo preview area"""
        try:
            # Show preview area
            self.photo_preview.opacity = 1
            
            # Update preview label with file info
            filename = file_path.split('/')[-1] if '/' in file_path else file_path
            file_size = "Unknown size"
            
            # Try to get file size
            try:
                import os
                if os.path.exists(file_path):
                    size_bytes = os.path.getsize(file_path)
                    if size_bytes < 1024:
                        file_size = f"{size_bytes} B"
                    elif size_bytes < 1024 * 1024:
                        file_size = f"{size_bytes // 1024} KB"
                    else:
                        file_size = f"{size_bytes // (1024 * 1024)} MB"
            except:
                pass
            
            self.preview_label.text = f"📷 {filename}\n📏 {file_size}"
            
        except Exception as e:
            self.preview_label.text = f"Photo Preview\nError: {str(e)}"
    
    def get_value(self):
        return self.photo_path
    
    def set_value(self, value):
        self.photo_path = value
        if value:
            self.photo_display.text = f"Photo: {value}"
            self._update_photo_preview(value)
        else:
            self.clear_photo(None)

    def get_content_height(self):
        values = self.get_responsive_values()
        # Base height: input + button + spacing
        base_height = values['input_height'] + values['button_height'] + dp(16)
        
        # Add preview height if photo is selected
        if self.photo_path and hasattr(self, 'photo_preview') and self.photo_preview.opacity > 0:
            base_height += dp(120) + dp(8)  # Preview height + spacing
        
        return base_height

class AudioRecordingField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "audio"
        self.audio_path = None
        self.is_recording = False
        self.create_audio_input()
        self.create_delete_button()
        self.update_field_height()

    def create_audio_input(self):
        self.audio_display = MDTextField(
            hint_text="No audio recorded",
            mode="rectangle",
            readonly=True,
            size_hint_y=None,
            height=dp(48)
        )
        self.button_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(48)
        )
        self.record_btn = MDRaisedButton(
            text="Start Recording",
            size_hint_x=0.7,
            on_release=self.toggle_recording
        )
        self.clear_btn = MDIconButton(
            icon="delete",
            size_hint_x=0.3,
            on_release=self.clear_audio
        )
        self.button_container.add_widget(self.record_btn)
        self.button_container.add_widget(self.clear_btn)
        self.add_widget(self.audio_display)
        self.add_widget(self.button_container)

    def toggle_recording(self, instance):
        if not self.is_recording:
            # Start recording
            self.is_recording = True
            self.record_btn.text = "Stop Recording"
            self.record_btn.md_bg_color = (1, 0.2, 0.2, 1)  # Red
            toast("Recording started...")
            
            # Simulate recording completion after 3 seconds
            Clock.schedule_once(self.stop_recording, 3)
        else:
            self.stop_recording()
    
    def stop_recording(self, dt=None):
        self.is_recording = False
        self.record_btn.text = "Start Recording"
        self.record_btn.md_bg_color = (0.2, 0.4, 0.8, 1)  # Default blue
        
        self.audio_path = f"audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        self.audio_display.text = f"Audio: {self.audio_path}"
        toast("Recording completed!")
    
    def clear_audio(self, instance):
        self.audio_path = None
        self.audio_display.text = ""
        self.audio_display.hint_text = "No audio recorded"
    
    def get_value(self):
        return self.audio_path
    
    def set_value(self, value):
        self.audio_path = value
        if value:
            self.audio_display.text = f"Audio: {value}"

    def get_content_height(self):
        values = self.get_responsive_values()
        return values['input_height'] + values['input_height'] + dp(8) + dp(48) + dp(48) + dp(2)

class BarcodeField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "barcode"
        self.barcode_value = None
        self.create_barcode_input()
        self.create_delete_button()
        self.update_field_height()

    def create_barcode_input(self):
        self.barcode_input = MDTextField(
            hint_text="Scan or enter barcode",
            mode="rectangle",
            size_hint_y=None,
            height=dp(48)
        )
        self.scan_btn = MDRaisedButton(
            text="Scan Barcode",
            size_hint_y=None,
            height=dp(36),
            on_release=self.scan_barcode
        )
        self.add_widget(self.barcode_input)
        self.add_widget(self.scan_btn)

    def scan_barcode(self, instance):
        # Simulate barcode scanning
        # In a real app, you'd use zbarcam or similar
        import random
        import string
        
        self.barcode_value = ''.join(random.choices(string.digits, k=12))
        self.barcode_input.text = self.barcode_value
        toast("Barcode scanned!")
    
    def get_value(self):
        return self.barcode_input.text or self.barcode_value
    
    def set_value(self, value):
        self.barcode_value = value
        self.barcode_input.text = str(value) if value else ""

    def get_content_height(self):
        values = self.get_responsive_values()
        return values['input_height'] + values['input_height'] + dp(8) + dp(48) + dp(36) + dp(2)

class GeoShapeField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "geoshape"
        self.shape_points = []
        self.create_geoshape_input()
        self.create_delete_button()
        self.update_field_height()

    def create_geoshape_input(self):
        """Create GPS area/polygon capture interface"""
        values = self.get_responsive_values()
        
        # Display field for area info
        self.area_input = MDTextField(
            hint_text="Tap to capture area boundary",
            mode="rectangle",
            size_hint_y=None,
            height=values['input_height'],
            font_size=values['font_size_secondary'],
            readonly=True
        )
        
        # Buttons for area capture
        self.button_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=values['button_height']
        )
        
        self.start_capture_btn = MDRaisedButton(
            text="Start Area Capture",
            size_hint_x=0.5,
            on_release=self.start_area_capture
        )
        
        self.clear_area_btn = MDRaisedButton(
            text="Clear Area",
            size_hint_x=0.5,
            on_release=self.clear_area
        )
        
        self.button_container.add_widget(self.start_capture_btn)
        self.button_container.add_widget(self.clear_area_btn)
        
        self.add_widget(self.area_input)
        self.add_widget(self.button_container)

    def start_area_capture(self, instance):
        """Start capturing area boundary points"""
        # Simulate area capture - in real app would use GPS tracking
        import random
        
        # Generate 4-6 random GPS points forming a rough polygon
        num_points = random.randint(4, 6)
        center_lat = random.uniform(-90, 90)
        center_lon = random.uniform(-180, 180)
        
        self.shape_points = []
        for i in range(num_points):
            # Generate points around center within ~1km radius
            lat_offset = random.uniform(-0.01, 0.01)
            lon_offset = random.uniform(-0.01, 0.01)
            point = {
                'latitude': round(center_lat + lat_offset, 6),
                'longitude': round(center_lon + lon_offset, 6)
            }
            self.shape_points.append(point)
        
        # Update display
        area_size = random.uniform(0.1, 5.0)  # Simulated area in hectares
        self.area_input.text = f"Area captured: {len(self.shape_points)} points, ~{area_size:.1f} hectares"
        toast(f"Area captured with {len(self.shape_points)} boundary points!")

    def clear_area(self, instance):
        """Clear captured area"""
        self.shape_points = []
        self.area_input.text = ""
        self.area_input.hint_text = "Tap to capture area boundary"
        toast("Area cleared")

    def get_value(self):
        """Return the captured area as a GeoJSON-like structure"""
        if not self.shape_points:
            return None
        
        return {
            'type': 'Polygon',
            'coordinates': [[
                [point['longitude'], point['latitude']] for point in self.shape_points
            ]],
            'properties': {
                'point_count': len(self.shape_points),
                'capture_method': 'mobile_gps'
            }
        }

    def set_value(self, value):
        """Set area value from saved data"""
        if value and isinstance(value, dict) and value.get('type') == 'Polygon':
            coordinates = value.get('coordinates', [[]])[0]
            self.shape_points = [
                {'latitude': coord[1], 'longitude': coord[0]} 
                for coord in coordinates
            ]
            point_count = len(self.shape_points)
            self.area_input.text = f"Area loaded: {point_count} boundary points"

    def get_content_height(self):
        values = self.get_responsive_values()
        return values['input_height'] + values['button_height'] + dp(16)

class VideoRecordingField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "video"
        self.video_path = None
        self.is_recording = False
        self.create_video_input()
        self.create_delete_button()
        self.update_field_height()

    def create_video_input(self):
        """Create video recording interface"""
        values = self.get_responsive_values()
        
        self.video_display = MDTextField(
            hint_text="No video recorded",
            mode="rectangle",
            readonly=True,
            size_hint_y=None,
            height=values['input_height'],
            font_size=values['font_size_secondary']
        )
        
        self.button_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=values['button_height']
        )
        
        self.record_btn = MDRaisedButton(
            text="Start Video Recording",
            size_hint_x=0.6,
            on_release=self.toggle_recording
        )
        
        self.gallery_btn = MDRaisedButton(
            text="Choose Video",
            size_hint_x=0.4,
            on_release=self.choose_from_gallery
        )
        
        self.button_container.add_widget(self.record_btn)
        self.button_container.add_widget(self.gallery_btn)
        
        self.add_widget(self.video_display)
        self.add_widget(self.button_container)

    def toggle_recording(self, instance):
        """Toggle video recording"""
        if not self.is_recording:
            # Start recording
            self.is_recording = True
            self.record_btn.text = "Stop Recording"
            self.record_btn.md_bg_color = (1, 0.2, 0.2, 1)  # Red
            toast("Video recording started...")
            
            # Simulate recording completion after 5 seconds
            Clock.schedule_once(self.stop_recording, 5)
        else:
            self.stop_recording()

    def stop_recording(self, dt=None):
        """Stop video recording"""
        self.is_recording = False
        self.record_btn.text = "Start Video Recording"
        self.record_btn.md_bg_color = (0.2, 0.4, 0.8, 1)  # Default blue
        
        self.video_path = f"video_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        duration = "0:05"  # Simulated duration
        self.video_display.text = f"Video: {self.video_path} ({duration})"
        toast("Video recording completed!")

    def choose_from_gallery(self, instance):
        """Choose video from gallery"""
        # Simulate choosing from gallery
        # In a real app, you'd use plyer.filechooser or similar
        self.video_path = f"gallery_video_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        self.video_display.text = f"Video: {self.video_path}"
        toast("Video selected from gallery!")

    def get_value(self):
        return self.video_path

    def set_value(self, value):
        self.video_path = value
        if value:
            self.video_display.text = f"Video: {value}"

    def get_content_height(self):
        values = self.get_responsive_values()
        return values['input_height'] + values['button_height'] + dp(16)

class FileUploadField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "file"
        self.file_path = None
        self.file_info = {}
        self.create_file_input()
        self.create_delete_button()
        self.update_field_height()

    def create_file_input(self):
        """Create file upload interface"""
        values = self.get_responsive_values()
        
        self.file_display = MDTextField(
            hint_text="No file selected",
            mode="rectangle",
            readonly=True,
            size_hint_y=None,
            height=values['input_height'],
            font_size=values['font_size_secondary']
        )
        
        self.button_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=values['button_height']
        )
        
        self.choose_btn = MDRaisedButton(
            text="Choose File",
            size_hint_x=0.6,
            on_release=self.choose_file
        )
        
        self.clear_btn = MDRaisedButton(
            text="Clear",
            size_hint_x=0.4,
            on_release=self.clear_file
        )
        
        self.button_container.add_widget(self.choose_btn)
        self.button_container.add_widget(self.clear_btn)
        
        # File type info
        self.info_label = MDLabel(
            text="Supported: PDF, DOC, XLS, TXT, images (max 50MB)",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20),
            font_size="12sp"
        )
        
        self.add_widget(self.file_display)
        self.add_widget(self.button_container)
        self.add_widget(self.info_label)

    def choose_file(self, instance):
        """Choose file for upload"""
        # Simulate file selection
        # In a real app, you'd use plyer.filechooser
        import random
        
        file_types = [
            ("document.pdf", "PDF Document", "156 KB"),
            ("spreadsheet.xlsx", "Excel Spreadsheet", "89 KB"),
            ("report.docx", "Word Document", "234 KB"),
            ("data.csv", "CSV Data", "45 KB"),
            ("image.jpg", "JPEG Image", "512 KB")
        ]
        
        filename, file_type, file_size = random.choice(file_types)
        self.file_path = f"uploads/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        self.file_info = {
            'filename': filename,
            'type': file_type,
            'size': file_size,
            'upload_date': datetime.datetime.now().isoformat()
        }
        
        self.file_display.text = f"{filename} ({file_size})"
        toast(f"File selected: {filename}")

    def clear_file(self, instance):
        """Clear selected file"""
        self.file_path = None
        self.file_info = {}
        self.file_display.text = ""
        self.file_display.hint_text = "No file selected"
        toast("File cleared")

    def get_value(self):
        """Return file information"""
        if not self.file_path:
            return None
        
        return {
            'file_path': self.file_path,
            'file_info': self.file_info
        }

    def set_value(self, value):
        """Set file value from saved data"""
        if value and isinstance(value, dict):
            self.file_path = value.get('file_path')
            self.file_info = value.get('file_info', {})
            
            if self.file_info.get('filename'):
                size = self.file_info.get('size', 'Unknown size')
                self.file_display.text = f"{self.file_info['filename']} ({size})"

    def get_content_height(self):
        values = self.get_responsive_values()
        return values['input_height'] + values['button_height'] + dp(20) + dp(16)

class DigitalSignatureField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "signature"
        self.signature_data = None
        self.create_signature_input()
        self.create_delete_button()
        self.update_field_height()

    def create_signature_input(self):
        """Create digital signature interface"""
        values = self.get_responsive_values()
        
        # Signature area placeholder
        self.signature_area = MDCard(
            size_hint_y=None,
            height=dp(120),
            md_bg_color=(0.95, 0.95, 0.95, 1),
            elevation=1
        )
        
        self.signature_placeholder = MDLabel(
            text="Signature Area\n(Tap 'Capture Signature' to sign)",
            halign="center",
            valign="center",
            theme_text_color="Secondary",
            font_size="14sp"
        )
        self.signature_area.add_widget(self.signature_placeholder)
        
        # Buttons
        self.button_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=values['button_height']
        )
        
        self.capture_btn = MDRaisedButton(
            text="Capture Signature",
            size_hint_x=0.6,
            on_release=self.capture_signature
        )
        
        self.clear_btn = MDRaisedButton(
            text="Clear",
            size_hint_x=0.4,
            on_release=self.clear_signature
        )
        
        self.button_container.add_widget(self.capture_btn)
        self.button_container.add_widget(self.clear_btn)
        
        self.add_widget(self.signature_area)
        self.add_widget(self.button_container)

    def capture_signature(self, instance):
        """Capture digital signature"""
        # Simulate signature capture
        # In a real app, you'd use a signature pad widget
        self.signature_data = {
            'signature_id': str(uuid.uuid4()),
            'captured_at': datetime.datetime.now().isoformat(),
            'signature_points': []  # Would contain actual signature stroke data
        }
        
        # Update display
        self.signature_placeholder.text = "✓ Signature Captured\n" + \
                                         datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        self.signature_area.md_bg_color = (0.9, 1.0, 0.9, 1)  # Light green
        toast("Signature captured successfully!")

    def clear_signature(self, instance):
        """Clear captured signature"""
        self.signature_data = None
        self.signature_placeholder.text = "Signature Area\n(Tap 'Capture Signature' to sign)"
        self.signature_area.md_bg_color = (0.95, 0.95, 0.95, 1)  # Default gray
        toast("Signature cleared")

    def get_value(self):
        return self.signature_data

    def set_value(self, value):
        if value and isinstance(value, dict):
            self.signature_data = value
            if value.get('captured_at'):
                self.signature_placeholder.text = "✓ Signature Captured\n" + value['captured_at']
                self.signature_area.md_bg_color = (0.9, 1.0, 0.9, 1)

    def get_content_height(self):
        values = self.get_responsive_values()
        return dp(120) + values['button_height'] + dp(16)

# Factory function to create form fields based on response type
def create_form_field(response_type, question_text="", options=None, **kwargs):
    """Factory function to create form fields based on response type"""
    field_map = {
        'text_short': ShortTextField,
        'text_long': LongTextField,
        'numeric_integer': NumericIntegerField,
        'numeric_decimal': NumericDecimalField,
        'choice_single': SingleChoiceField,
        'choice_multiple': MultipleChoiceField,
        'scale_rating': RatingScaleField,
        'date': DateField,
        'datetime': DateTimeField,
        'geopoint': LocationPickerField,
        'geoshape': GeoShapeField,
        'image': PhotoUploadField,
        'audio': AudioRecordingField,
        'video': VideoRecordingField,
        'file': FileUploadField,
        'signature': DigitalSignatureField,
        'barcode': BarcodeField,
    }
    
    field_class = field_map.get(response_type, ShortTextField)
    print(f"Creating field class: {field_class}")
    # Only pass options to choice fields
    if response_type in ['choice_single', 'choice_multiple']:
        field = field_class(question_text=question_text, options=options, **kwargs)
    else:
        field = field_class(question_text=question_text, **kwargs)
    return field

