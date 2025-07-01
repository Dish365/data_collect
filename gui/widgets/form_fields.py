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
        """Update layout properties based on screen size"""
        values = self.get_responsive_values()
        
        # Update card properties
        self.padding = values['padding']
        self.spacing = values['spacing']
        self.size_hint_y = None
        self.height = values['height']
        self.md_bg_color = (1, 1, 1, 1)  # Pure white background
        self.elevation = 1  # Subtle shadow
        
        # Update existing children if they exist
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
        """Create responsive header section"""
        values = self.get_responsive_values()
        
        self.header_card = MDCard(
            orientation='horizontal',
            size_hint_y=None,
            height=values['header_height'],
            padding=values['padding'] * 0.6,  # Proportional padding
            spacing=dp(12),
            md_bg_color=(0.95, 0.95, 0.95, 1),  # Light gray background
            elevation=0
        )
        
        self.question_number_label = MDLabel(
            text=f"Question {self.question_number}",
            font_style="Subtitle1",
            theme_text_color="Primary",
            bold=True,
            size_hint_x=None,
            width=dp(120),  # Slightly wider for tablets
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

class ShortTextField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "text_short"
        
        # Create responsive text input
        self.create_text_input()
    
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

class LongTextField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "text_long"
        
        # Create responsive multiline text input
        self.create_text_input()
    
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

class NumericIntegerField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "numeric_integer"
        
        # Create responsive numeric input
        self.create_numeric_input()
    
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

class NumericDecimalField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "numeric_decimal"
        
        # Create responsive decimal input
        self.create_decimal_input()
    
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

class SingleChoiceField(BaseFormField):
    options = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "choice_single"
        self.selected_option = None
        self.checkboxes = []
        
        # Create responsive options management
        self.create_options_header()
        self.create_options_container()
        
        # Initialize with default options if none provided
        if not self.options:
            self.options = ['Option 1', 'Option 2']
        
        # Update height based on options and screen size
        self.update_field_height()
    
    def create_options_header(self):
        """Create responsive options management header"""
        values = self.get_responsive_values()
        
        self.options_header = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(12),  # Increased spacing for tablets
            size_hint_y=None,
            height=values['button_height']
        )
        
        self.options_label = MDLabel(
            text="Options:",
            size_hint_x=0.3,
            font_style="Subtitle2",
            theme_text_color="Primary",
            font_size=values['font_size_secondary']
        )
        
        # Tablet-optimized buttons with larger touch targets
        self.add_option_btn = MDRaisedButton(
            text="Add Option",
            size_hint_x=0.35,
            size_hint_y=None,
            height=values['button_height'],
            font_size=values['font_size_small'],
            on_release=self.add_option
        )
        
        self.remove_option_btn = MDRaisedButton(
            text="Remove Last",
            size_hint_x=0.35,
            size_hint_y=None,
            height=values['button_height'],
            font_size=values['font_size_small'],
            on_release=self.remove_last_option
        )
        
        self.options_header.add_widget(self.options_label)
        self.options_header.add_widget(self.add_option_btn)
        self.options_header.add_widget(self.remove_option_btn)
        self.add_widget(self.options_header)
    
    def create_options_container(self):
        """Create responsive options container with multi-column support"""
        self.options_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(12),  # Increased spacing for tablets
            size_hint_y=None,
            adaptive_height=True
        )
        self.add_widget(self.options_container)
    
    def get_optimal_columns(self):
        """Get optimal number of columns based on screen size and option count"""
        if not self.responsive_helper:
            return 1  # Fallback to single column
        
        category = self.responsive_helper.get_screen_size_category()
        is_landscape = self.responsive_helper.is_landscape()
        option_count = len(self.options)
        
        # Column calculation based on screen size
        if category == "large_tablet":
            max_cols = 3 if is_landscape else 2
        elif category == "tablet":
            max_cols = 2 if is_landscape else 2
        elif category == "small_tablet":
            max_cols = 2 if is_landscape else 1
        else:  # phone
            max_cols = 1
        
        # Don't use more columns than we have options
        return min(max_cols, option_count, 3)  # Cap at 3 columns max
    
    def _on_window_resize(self, *args):
        """Handle window resize"""
        super()._on_window_resize(*args)
        self.update_options_layout()
        self.update_button_sizes()
    
    def update_button_sizes(self):
        """Update button sizes for responsive design"""
        if not hasattr(self, 'options_header'):
            return
        
        values = self.get_responsive_values()
        
        # Update header buttons
        if hasattr(self, 'add_option_btn'):
            self.add_option_btn.height = values['button_height']
            self.add_option_btn.font_size = values['font_size_small']
        
        if hasattr(self, 'remove_option_btn'):
            self.remove_option_btn.height = values['button_height']
            self.remove_option_btn.font_size = values['font_size_small']
        
        if hasattr(self, 'options_label'):
            self.options_label.font_size = values['font_size_secondary']
    
    def update_field_height(self):
        """Update field height based on options and screen size"""
        values = self.get_responsive_values()
        cols = self.get_optimal_columns()
        
        # Calculate rows needed
        rows = (len(self.options) + cols - 1) // cols  # Ceiling division
        
        # Base height + option rows
        option_height = values['button_height'] + dp(12)  # Button height + spacing
        total_option_height = rows * option_height
        
        self.height = values['height'] + total_option_height
    
    def add_option(self, instance):
        """Add a new option to the choice field"""
        new_option = f"Option {len(self.options) + 1}"
        self.options = self.options + [new_option]
        toast("Option added. You can edit the option text directly.")
    
    def remove_last_option(self, instance):
        """Remove the last option from the choice field"""
        if len(self.options) > 2:  # Keep at least 2 options
            self.options = self.options[:-1]
            toast("Option removed.")
        else:
            toast("Single choice questions need at least 2 options.")
    
    def on_options(self, instance, options):
        """Handle options list changes with responsive layout"""
        self.options_container.clear_widgets()
        self.checkboxes = []
        
        if not options:
            return
        
        self.update_options_layout()
        self.update_field_height()
    
    def update_options_layout(self):
        """Update options layout with responsive multi-column support"""
        self.options_container.clear_widgets()
        self.checkboxes = []
        
        if not self.options:
            return
        
        values = self.get_responsive_values()
        cols = self.get_optimal_columns()
        
        if cols == 1:
            # Single column layout
            self.create_single_column_options(values)
        else:
            # Multi-column layout for tablets
            self.create_multi_column_options(values, cols)
    
    def create_single_column_options(self, values):
        """Create single column options layout"""
        for i, option in enumerate(self.options):
            row = self.create_option_row(i, option, values)
            self.options_container.add_widget(row)
    
    def create_multi_column_options(self, values, cols):
        """Create multi-column options layout for tablets"""
        # Group options into rows
        for row_start in range(0, len(self.options), cols):
            row_options = self.options[row_start:row_start + cols]
            
            # Create horizontal container for this row
            row_container = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(16),  # Space between columns
                size_hint_y=None,
                height=values['button_height'] + dp(8),
                adaptive_width=True
            )
            
            # Add options to this row
            for i, option in enumerate(row_options):
                option_index = row_start + i
                option_widget = self.create_option_widget(option_index, option, values)
                option_widget.size_hint_x = 1 / len(row_options)  # Equal width
                row_container.add_widget(option_widget)
            
            self.options_container.add_widget(row_container)
    
    def create_option_row(self, index, option, values):
        """Create a single option row"""
        row = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(12),
            size_hint_y=None,
            height=values['button_height'] + dp(8)
        )
        
        option_widget = self.create_option_widget(index, option, values)
        row.add_widget(option_widget)
        return row
    
    def create_option_widget(self, index, option, values):
        """Create an individual option widget"""
        option_container = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(12),
            size_hint_y=None,
            height=values['button_height']
        )
        
        checkbox = MDCheckbox(
            group="single_choice",
            size_hint=(None, None),
            size=(dp(32), dp(32)),  # Larger checkbox for tablets
            on_active=lambda x, active, opt=option: self.on_option_selected(opt, active)
        )
        
        # Make option text editable with responsive sizing
        option_input = MDTextField(
            text=option,
            size_hint_x=0.8,
            font_size=values['font_size_secondary'],
            height=values['input_height'],
            size_hint_y=None,
            mode="rectangle",
            on_text_validate=lambda instance, idx=index: self.update_option(idx, instance.text)
        )
        option_input.bind(on_text_validate=lambda instance, idx=index: self.update_option(idx, instance.text))
        
        option_container.add_widget(checkbox)
        option_container.add_widget(option_input)
        self.checkboxes.append(checkbox)
        
        return option_container
    
    def on_option_selected(self, option, active):
        if active:
            self.selected_option = option
    
    def update_option(self, index, new_text):
        """Update an option text"""
        if 0 <= index < len(self.options) and new_text.strip():
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

class MultipleChoiceField(BaseFormField):
    options = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "choice_multiple"
        self.selected_options = []
        self.checkboxes = []
        
        # Add options management section
        self.options_header = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40)
        )
        
        self.options_label = MDLabel(
            text="Options:",
            size_hint_x=0.3,
            font_style="Subtitle2",
            theme_text_color="Primary"
        )
        
        self.add_option_btn = MDRaisedButton(
            text="Add Option",
            size_hint_x=0.35,
            size_hint_y=None,
            height=dp(32),
            font_size="12sp",
            on_release=self.add_option
        )
        
        self.remove_option_btn = MDRaisedButton(
            text="Remove Last",
            size_hint_x=0.35,
            size_hint_y=None,
            height=dp(32),
            font_size="12sp",
            on_release=self.remove_last_option
        )
        
        self.options_header.add_widget(self.options_label)
        self.options_header.add_widget(self.add_option_btn)
        self.options_header.add_widget(self.remove_option_btn)
        self.add_widget(self.options_header)
        
        self.options_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
            adaptive_height=True
        )
        self.add_widget(self.options_container)
        
        # Initialize with default options if none provided
        if not self.options:
            self.options = ['Option 1', 'Option 2']
        
        # Update height based on options
        self.height = dp(160 + len(self.options) * 40)
    
    def add_option(self, instance):
        """Add a new option to the choice field"""
        new_option = f"Option {len(self.options) + 1}"
        self.options = self.options + [new_option]
        toast("Option added. You can edit the option text directly.")
    
    def remove_last_option(self, instance):
        """Remove the last option from the choice field"""
        if len(self.options) > 2:  # Keep at least 2 options
            self.options = self.options[:-1]
            toast("Option removed.")
        else:
            toast("Multiple choice questions need at least 2 options.")
    
    def on_options(self, instance, options):
        self.options_container.clear_widgets()
        self.checkboxes = []
        
        for i, option in enumerate(options):
            row = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(40)
            )
            
            checkbox = MDCheckbox(
                size_hint=(None, None),
                size=(dp(24), dp(24)),
                on_active=lambda x, active, opt=option: self.on_option_selected(opt, active)
            )
            
            # Make option text editable
            option_input = MDTextField(
                text=option,
                size_hint_x=0.8,
                font_size="14sp",
                height=dp(32),
                size_hint_y=None,
                mode="rectangle",
                on_text_validate=lambda instance, idx=i: self.update_option(idx, instance.text)
            )
            option_input.bind(on_text_validate=lambda instance, idx=i: self.update_option(idx, instance.text))
            
            row.add_widget(checkbox)
            row.add_widget(option_input)
            self.options_container.add_widget(row)
            self.checkboxes.append(checkbox)
        
        # Update height
        self.height = dp(160 + len(options) * 40)
    
    def update_option(self, index, new_text):
        """Update an option text"""
        if 0 <= index < len(self.options) and new_text.strip():
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

class DateField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "date"
        self.selected_date = None

        self.date_input = MDTextField(
            hint_text="Tap to select date",
            mode="rectangle",
            readonly=True,
            size_hint_y=None,
            height=dp(48),
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

class DateTimeField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "datetime"
        self.selected_date = None
        self.selected_time = None
        self.height = dp(180)  # Increased for question input + two date fields

        self.date_input = MDTextField(
            hint_text="Tap to select date",
            mode="rectangle",
            readonly=True,
            size_hint_y=None,
            height=dp(48),
            on_focus=self.show_date_picker
        )
        
        self.time_input = MDTextField(
            hint_text="Tap to select time",
            mode="rectangle",
            readonly=True,
            size_hint_y=None,
            height=dp(48),
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

class LocationPickerField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "geopoint"
        self.current_location = None
        self.height = dp(180)  # Increased for question input + location fields

        self.location_display = MDTextField(
            hint_text="No location selected",
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
        
        self.get_location_btn = MDRaisedButton(
            text="Get Current Location",
            size_hint_x=0.7,
            on_release=self.get_current_location
        )
        
        self.clear_btn = MDIconButton(
            icon="delete",
            size_hint_x=0.3,
            on_release=self.clear_location
        )
        
        self.button_container.add_widget(self.get_location_btn)
        self.button_container.add_widget(self.clear_btn)

        self.add_widget(self.location_display)
        self.add_widget(self.button_container)
    
    def get_current_location(self, instance):
        # Simulate getting GPS location
        # In a real app, you'd use plyer.gps or similar
        import random
        lat = round(random.uniform(-90, 90), 6)
        lon = round(random.uniform(-180, 180), 6)
        
        self.current_location = {'latitude': lat, 'longitude': lon}
        self.location_display.text = f"Lat: {lat}, Lon: {lon}"
        toast("Location captured!")
    
    def clear_location(self, instance):
        self.current_location = None
        self.location_display.text = ""
        self.location_display.hint_text = "No location selected"
    
    def get_value(self):
        return self.current_location
    
    def set_value(self, value):
        if value and isinstance(value, dict):
            self.current_location = value
            lat = value.get('latitude', 0)
            lon = value.get('longitude', 0)
            self.location_display.text = f"Lat: {lat}, Lon: {lon}"

class PhotoUploadField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "image"
        self.photo_path = None
        self.height = dp(180)  # Increased for question input + photo fields
        
        self.photo_display = MDTextField(
            hint_text="No photo selected",
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
        
        self.camera_btn = MDRaisedButton(
            text="Take Photo",
            size_hint_x=0.5,
            on_release=self.take_photo
        )
        
        self.gallery_btn = MDRaisedButton(
            text="Choose from Gallery",
            size_hint_x=0.5,
            on_release=self.choose_from_gallery
        )
        
        self.button_container.add_widget(self.camera_btn)
        self.button_container.add_widget(self.gallery_btn)

        self.add_widget(self.photo_display)
        self.add_widget(self.button_container)
    
    def take_photo(self, instance):
        # Simulate taking a photo
        # In a real app, you'd use plyer.camera or similar
        self.photo_path = f"photo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        self.photo_display.text = f"Photo: {self.photo_path}"
        toast("Photo captured!")
    
    def choose_from_gallery(self, instance):
        # Simulate choosing from gallery
        # In a real app, you'd use plyer.filechooser or similar
        self.photo_path = f"gallery_photo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        self.photo_display.text = f"Photo: {self.photo_path}"
        toast("Photo selected!")
    
    def get_value(self):
        return self.photo_path
    
    def set_value(self, value):
        self.photo_path = value
        if value:
            self.photo_display.text = f"Photo: {value}"

class AudioRecordingField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "audio"
        self.audio_path = None
        self.is_recording = False
        self.height = dp(180)  # Increased for question input + audio fields
        
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

class BarcodeField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "barcode"
        self.barcode_value = None

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
        'image': PhotoUploadField,
        'audio': AudioRecordingField,
        'barcode': BarcodeField,
    }
    
    field_class = field_map.get(response_type, ShortTextField)
    field = field_class(question_text=question_text, **kwargs)
    
    # Set options for choice fields
    if hasattr(field, 'options') and options:
        field.options = options
    
    return field

