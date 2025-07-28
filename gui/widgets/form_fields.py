from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivymd.uix.card import MDCard
from kivymd.uix.pickers import MDModalDatePicker, MDModalInputDatePicker, MDTimePickerDialVertical, MDTimePickerDialHorizontal
from utils.cross_platform_toast import toast
from kivy.clock import Clock
from kivy.core.window import Window
import datetime
import uuid

# Load the modern KV file for form fields
from kivy.lang import Builder
Builder.load_file("kv/form_fields.kv")

# Helper function to create modern buttons (only used internally if needed)
def create_modern_button(text="Button", icon="plus", style="filled", color=(0.2, 0.6, 1.0, 1), size=(100, 36), **kwargs):
    """Helper for any remaining dynamic button creation - mostly handled by KV now"""
    from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
    from kivy.metrics import dp
    
    button = MDButton(
        style=style,
        md_bg_color=color,
        size_hint=(None, None),
        size=size,
        **kwargs
    )
    
    button_icon = MDButtonIcon(icon=icon)
    button_text = MDButtonText(text=text, font_size="12sp")
    
    button.add_widget(button_icon)
    button.add_widget(button_text)
    
    return button

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
        
        # Update responsive layout
        self.update_responsive_layout()
        
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
        from kivy.metrics import dp
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
        from kivy.metrics import dp
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
        # All widgets are now handled by KV - minimal updates needed
        pass
    
    def get_response_type_display(self):
        """Get display name for response type"""
        type_map = {
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
            'image': 'Photo',
            'audio': 'Audio',
            'barcode': 'Barcode'
        }
        return type_map.get(self.response_type, self.response_type.replace('_', ' ').title())
        
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
        if hasattr(self.ids, 'question_input'):
            return self.ids.question_input.text.strip()
        return self.question_text
        
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
        from kivy.metrics import dp
        return dp(40)

    def update_field_height(self):
        from kivy.metrics import dp
        values = self.get_responsive_values()
        extra_padding = dp(24)
        self.height = values['height'] + self.get_content_height() + extra_padding

    def create_delete_button(self):
        # Delete button is now handled by KV file
        pass

# All field classes now simplified - UI handled by KV
class ShortTextField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "text_short"

    def get_value(self):
        if hasattr(self.ids, 'question_input'):
            return self.ids.question_input.text.strip()
        return ""

    def set_value(self, value):
        if hasattr(self.ids, 'question_input'):
            self.ids.question_input.text = str(value)

class LongTextField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "text_long"

    def get_value(self):
        if hasattr(self.ids, 'question_input'):
            return self.ids.question_input.text.strip()
        return ""

    def set_value(self, value):
        if hasattr(self.ids, 'question_input'):
            self.ids.question_input.text = str(value)

class NumericIntegerField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "numeric_integer"

    def get_value(self):
        if hasattr(self.ids, 'question_input'):
            try:
                value = self.ids.question_input.text.strip()
                return int(value) if value else None
            except ValueError:
                return None
        return None

    def set_value(self, value):
        if hasattr(self.ids, 'question_input'):
            self.ids.question_input.text = str(value) if value is not None else ""

    def validate(self):
        is_valid, errors = super().validate()
        value = self.get_value()
        if hasattr(self.ids, 'question_input') and self.ids.question_input.text.strip() and value is None:
            errors.append("Please enter a valid whole number")
            is_valid = False
        return is_valid, errors

class NumericDecimalField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "numeric_decimal"

    def get_value(self):
        if hasattr(self.ids, 'question_input'):
            try:
                value = self.ids.question_input.text.strip()
                return float(value) if value else None
            except ValueError:
                return None
        return None

    def set_value(self, value):
        if hasattr(self.ids, 'question_input'):
            self.ids.question_input.text = str(value) if value is not None else ""

    def validate(self):
        is_valid, errors = super().validate()
        value = self.get_value()
        if hasattr(self.ids, 'question_input') and self.ids.question_input.text.strip() and value is None:
            errors.append("Please enter a valid decimal number")
            is_valid = False
        return is_valid, errors

class SingleChoiceField(BaseFormField):
    options = ListProperty([])

    def __init__(self, question_text="", options=None, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "choice_single"
        self.selected_option = None
        self.options = options if options else ['Option 1', 'Option 2']

    def on_options(self, instance, options):
        # Options management is now handled by KV file
        pass
    
    def add_option(self):
        new_option = f"Option {len(self.options) + 1}"
        self.options = self.options + [new_option]
        toast("Option added.")
    
    def remove_option(self):
        if len(self.options) > 2:
            self.options = self.options[:-1]
            toast("Option removed.")
        else:
            toast("Single choice questions need at least 2 options.")
    
    def on_option_selected(self, option, active):
        if active:
            self.selected_option = option
    
    def get_value(self):
        return self.selected_option
    
    def set_value(self, value):
        self.selected_option = value
    
    def validate(self):
        is_valid, errors = super().validate()
        if len(self.options) < 2:
            errors.append("Single choice questions need at least 2 options")
            is_valid = False
        return is_valid, errors

    def get_content_height(self):
        from kivy.metrics import dp
        return dp(100) + len(self.options) * dp(40)

class MultipleChoiceField(BaseFormField):
    options = ListProperty([])

    def __init__(self, question_text="", options=None, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "choice_multiple"
        self.selected_options = []
        self.options = options if options else ['Option 1', 'Option 2']

    def on_options(self, instance, options):
        # Options management is now handled by KV file
        pass
    
    def add_option(self):
        new_option = f"Option {len(self.options) + 1}"
        self.options = self.options + [new_option]
        toast("Option added.")

    def remove_option(self):
        if len(self.options) > 2:
            self.options = self.options[:-1]
            toast("Option removed.")
        else:
            toast("Multiple choice questions need at least 2 options.")
    
    def on_option_selected(self, option, active):
        if active and option not in self.selected_options:
            self.selected_options.append(option)
        elif not active and option in self.selected_options:
            self.selected_options.remove(option)
    
    def get_value(self):
        return self.selected_options
    
    def set_value(self, value):
        self.selected_options = value if isinstance(value, list) else []
    
    def validate(self):
        is_valid, errors = super().validate()
        if len(self.options) < 2:
            errors.append("Multiple choice questions need at least 2 options")
            is_valid = False
        return is_valid, errors

    def get_content_height(self):
        from kivy.metrics import dp
        return dp(100) + len(self.options) * dp(40)

class RatingScaleField(BaseFormField):
    min_value = NumericProperty(1)
    max_value = NumericProperty(5)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "scale_rating"
        self.current_value = self.min_value

    def on_slider_value(self, instance, value):
        self.current_value = int(value)
    
    def get_value(self):
        return self.current_value
    
    def set_value(self, value):
        if value is not None:
            self.current_value = int(value)

    def get_content_height(self):
        from kivy.metrics import dp
        return dp(60)

class DateField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "date"
        self.selected_date = None

    def show_date_picker(self, instance, focus):
        if focus:
            date_dialog = MDModalDatePicker()
            date_dialog.bind(on_ok=self.set_date)
            date_dialog.open()
    
    def set_date(self, instance, date_obj, *_):
        self.selected_date = date_obj
        instance.dismiss()
    
    def get_value(self):
        return self.selected_date.strftime('%Y-%m-%d') if self.selected_date else None
    
    def set_value(self, value):
        if value:
            try:
                self.selected_date = datetime.datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                pass

class DateTimeField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "datetime"
        self.selected_date = None
        self.selected_time = None

    def show_date_picker(self, instance, focus):
        if focus:
            date_dialog = MDModalDatePicker()
            date_dialog.bind(on_ok=self.set_date)
            date_dialog.open()
    
    def show_time_picker(self, instance, focus):
        if focus:
            time_dialog = MDTimePickerDialVertical()
            time_dialog.bind(on_save=self.set_time)
            time_dialog.open()

    def set_date(self, instance, date_obj, *_):
        self.selected_date = date_obj
        instance.dismiss()
    
    def set_time(self, instance, time_obj, *_):
        self.selected_time = time_obj
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
            except ValueError:
                pass

    def get_content_height(self):
        from kivy.metrics import dp
        return dp(80)

class LocationPickerField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "geopoint"
        self.current_location = None
        self.gps_accuracy = None
        self.is_getting_location = False

    def get_current_location(self):
        if self.is_getting_location:
            return
        self.is_getting_location = True
        toast("Getting GPS location...")
        Clock.schedule_once(self._simulate_gps_result, 2)
    
    def _simulate_gps_result(self, dt):
        import random
        base_lat, base_lon = 45.5017, -73.5673
        lat = round(base_lat + random.uniform(-0.01, 0.01), 6)
        lon = round(base_lon + random.uniform(-0.01, 0.01), 6)
        accuracy = round(random.uniform(3.0, 15.0), 1)
        
        self.current_location = {
            'latitude': lat, 'longitude': lon, 'accuracy': accuracy,
            'timestamp': datetime.datetime.now().isoformat(), 'provider': 'gps'
        }
        self.gps_accuracy = accuracy
        self.is_getting_location = False
        toast(f"Location captured with {accuracy}m accuracy!")
    
    def clear_location(self):
        self.current_location = None
        self.gps_accuracy = None
        toast("Location cleared")
    
    def get_value(self):
        return self.current_location
    
    def set_value(self, value):
        if value and isinstance(value, dict):
            self.current_location = value

    def get_content_height(self):
        from kivy.metrics import dp
        return dp(100)

# Simplified versions of remaining field classes
class PhotoUploadField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "image"
        self.photo_path = None

    def take_photo(self):
        self.photo_path = f"photo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        toast("Photo captured!")
    
    def choose_from_gallery(self):
        self.photo_path = f"gallery_photo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        toast("Photo selected!")
    
    def clear_photo(self):
        self.photo_path = None
        toast("Photo cleared")
    
    def get_value(self):
        return self.photo_path
    
    def set_value(self, value):
        self.photo_path = value

    def get_content_height(self):
        from kivy.metrics import dp
        return dp(120)

class AudioRecordingField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "audio"
        self.audio_path = None
        self.is_recording = False

    def toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            toast("Recording started...")
            Clock.schedule_once(self.stop_recording, 3)
        else:
            self.stop_recording()
    
    def stop_recording(self, dt=None):
        self.is_recording = False
        self.audio_path = f"audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        toast("Recording completed!")
    
    def clear_audio(self):
        self.audio_path = None
        toast("Audio cleared")
    
    def get_value(self):
        return self.audio_path
    
    def set_value(self, value):
        self.audio_path = value

class BarcodeField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "barcode"
        self.barcode_value = None

    def scan_barcode(self):
        import random, string
        self.barcode_value = ''.join(random.choices(string.digits, k=12))
        toast("Barcode scanned!")
    
    def get_value(self):
        return self.barcode_value
    
    def set_value(self, value):
        self.barcode_value = value

class GeoShapeField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "geoshape"
        self.shape_points = []

    def start_area_capture(self):
        import random
        self.shape_points = [
            {'latitude': random.uniform(-90, 90), 'longitude': random.uniform(-180, 180)}
            for _ in range(random.randint(4, 6))
        ]
        toast(f"Area captured with {len(self.shape_points)} boundary points!")

    def clear_area(self):
        self.shape_points = []
        toast("Area cleared")

    def get_value(self):
        if not self.shape_points:
            return None
        return {
            'type': 'Polygon',
            'coordinates': [[[p['longitude'], p['latitude']] for p in self.shape_points]],
            'properties': {'point_count': len(self.shape_points), 'capture_method': 'mobile_gps'}
        }

    def set_value(self, value):
        if value and isinstance(value, dict) and value.get('type') == 'Polygon':
            coordinates = value.get('coordinates', [[]])[0]
            self.shape_points = [
                {'latitude': coord[1], 'longitude': coord[0]} for coord in coordinates
            ]

class VideoRecordingField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "video"
        self.video_path = None
        self.is_recording = False

    def toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            toast("Video recording started...")
            Clock.schedule_once(self.stop_recording, 5)
        else:
            self.stop_recording()

    def stop_recording(self, dt=None):
        self.is_recording = False
        self.video_path = f"video_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        toast("Video recording completed!")

    def choose_from_gallery(self):
        self.video_path = f"gallery_video_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        toast("Video selected from gallery!")

    def get_value(self):
        return self.video_path

    def set_value(self, value):
        self.video_path = value

class FileUploadField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "file"
        self.file_path = None
        self.file_info = {}

    def choose_file(self):
        import random
        file_types = [
            ("document.pdf", "PDF Document", "156 KB"),
            ("spreadsheet.xlsx", "Excel Spreadsheet", "89 KB"),
            ("report.docx", "Word Document", "234 KB"),
        ]
        filename, file_type, file_size = random.choice(file_types)
        self.file_path = f"uploads/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        self.file_info = {
            'filename': filename, 'type': file_type, 'size': file_size,
            'upload_date': datetime.datetime.now().isoformat()
        }
        toast(f"File selected: {filename}")

    def clear_file(self):
        self.file_path = None
        self.file_info = {}
        toast("File cleared")

    def get_value(self):
        if not self.file_path:
            return None
        return {'file_path': self.file_path, 'file_info': self.file_info}

    def set_value(self, value):
        if value and isinstance(value, dict):
            self.file_path = value.get('file_path')
            self.file_info = value.get('file_info', {})

class DigitalSignatureField(BaseFormField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_type = "signature"
        self.signature_data = None

    def capture_signature(self):
        self.signature_data = {
            'signature_id': str(uuid.uuid4()),
            'captured_at': datetime.datetime.now().isoformat(),
            'signature_points': []
        }
        toast("Signature captured successfully!")

    def clear_signature(self):
        self.signature_data = None
        toast("Signature cleared")

    def get_value(self):
        return self.signature_data

    def set_value(self, value):
        if value and isinstance(value, dict):
            self.signature_data = value

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
    
    # Only pass options to choice fields
    if response_type in ['choice_single', 'choice_multiple']:
        field = field_class(question_text=question_text, options=options, **kwargs)
    else:
        field = field_class(question_text=question_text, **kwargs)
    return field

