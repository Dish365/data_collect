from kivymd.uix.card import MDCard
from kivy.properties import ObjectProperty, StringProperty
from kivy.event import EventDispatcher
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.core.window import Window
import json

# Load the KV file
Builder.load_file("kv/question_widget.kv")


class QuestionWidget(MDCard, EventDispatcher):
    """Modern question widget using KivyMD 2.0.1 Material Design"""
    
    question_data = ObjectProperty()
    question_id = StringProperty('')
    question_text = StringProperty('')
    question_type = StringProperty('')
    options = StringProperty('[]')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_delete')
        
        # Setup responsive properties
        self.update_responsive_properties()
        
        # Bind to window resize for responsive updates
        Window.bind(on_resize=self._on_window_resize)
        
        # Bind properties
        self.bind(question_text=self._update_question_text)
        self.bind(question_type=self._update_question_type)
        self.bind(options=self._update_options)
    
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
                self.height = dp(200)
                self.padding = [dp(20), dp(16)]
                self.spacing = dp(12)
            elif category == "tablet":
                self.height = dp(180)
                self.padding = [dp(16), dp(12)]
                self.spacing = dp(10)
            elif category == "small_tablet":
                self.height = dp(160)
                self.padding = [dp(14), dp(10)]
                self.spacing = dp(8)
            else:  # phone
                self.height = dp(150)
                self.padding = [dp(12), dp(8)]
                self.spacing = dp(6)
                
        except Exception as e:
            print(f"Error updating QuestionWidget responsive properties: {e}")
            # Fallback to default values
            self.height = dp(150)
            self.padding = [dp(12), dp(8)]
            self.spacing = dp(6)
    
    def _update_question_text(self, instance, value):
        """Update question text in UI"""
        if hasattr(self, 'question_label'):
            self.question_label.text = value
    
    def _update_question_type(self, instance, value):
        """Update question type and recreate response widget"""
        self._create_response_widget()
    
    def _update_options(self, instance, value):
        """Update options for select/multiselect questions"""
        if self.question_type in ['select', 'multiselect']:
            self._create_response_widget()
    
    def _create_response_widget(self):
        """Create appropriate response widget based on question type using KV"""
        if not hasattr(self, 'response_area'):
            return
            
        # Clear existing widgets
        self.response_area.clear_widgets()
        
        # Create appropriate widget based on question type using KV
        from kivy.lang import Builder
        
        widget_map = {
            'text': 'TextResponseWidget',
            'number': 'NumberResponseWidget', 
            'select': 'SelectResponseWidget',
            'multiselect': 'MultiSelectResponseWidget',
            'date': 'DateResponseWidget',
            'time': 'TimeResponseWidget',
            'datetime': 'DateTimeResponseWidget',
        }
        
        widget_class = widget_map.get(self.question_type, 'TextResponseWidget')
        
        widget = Builder.load_string(f'''
{widget_class}:
    question_options: {self.options}
''')
        
        self.response_area.add_widget(widget)
        self.response_widget = widget
    
    def get_response(self):
        """Get the current response value"""
        if not hasattr(self, 'response_widget'):
            return ''
            
        if self.question_type == 'text':
            return self.response_widget.text
        elif self.question_type == 'number':
            return self.response_widget.text
        elif self.question_type == 'select':
            return self.response_widget.text
        elif self.question_type == 'multiselect':
            selected = []
            for checkbox, option in self.checkboxes:
                if checkbox.active:
                    selected.append(option)
            return json.dumps(selected)
        return ''
    
    def clear_response(self):
        """Clear the current response"""
        if not hasattr(self, 'response_widget'):
            return
            
        if self.question_type == 'text':
            self.response_widget.text = ''
        elif self.question_type == 'number':
            self.response_widget.text = ''
        elif self.question_type == 'select':
            self.response_widget.text = 'Select an option'
        elif self.question_type == 'multiselect':
            for checkbox, _ in self.checkboxes:
                checkbox.active = False

    def get_data(self):
        """Return the question's data"""
        return self.question_data

    def on_delete(self, *args):
        """Handle delete event"""
        pass 