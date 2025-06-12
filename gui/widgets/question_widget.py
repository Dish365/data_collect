from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.properties import StringProperty
import json

class QuestionWidget(BoxLayout):
    question_id = StringProperty('')
    question_text = StringProperty('')
    question_type = StringProperty('')
    options = StringProperty('[]')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(150)
        
        # Question text
        self.text_label = Label(
            text=self.question_text,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16)
        )
        self.add_widget(self.text_label)
        
        # Response input
        self.response_widget = self._create_response_widget()
        self.add_widget(self.response_widget)
        
        # Bind properties
        self.bind(question_text=self.text_label.setter('text'))
    
    def _create_response_widget(self):
        """Create appropriate response widget based on question type"""
        if self.question_type == 'text':
            return TextInput(
                multiline=False,
                size_hint_y=None,
                height=dp(40)
            )
        elif self.question_type == 'number':
            return TextInput(
                multiline=False,
                input_filter='float',
                size_hint_y=None,
                height=dp(40)
            )
        elif self.question_type == 'select':
            options = json.loads(self.options)
            spinner = Spinner(
                text='Select an option',
                values=options,
                size_hint_y=None,
                height=dp(40)
            )
            return spinner
        elif self.question_type == 'multiselect':
            options = json.loads(self.options)
            layout = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(len(options) * 40)
            )
            self.checkboxes = []
            for option in options:
                option_layout = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(40)
                )
                checkbox = CheckBox(size_hint_x=None, width=dp(40))
                label = Label(text=option)
                option_layout.add_widget(checkbox)
                option_layout.add_widget(label)
                layout.add_widget(option_layout)
                self.checkboxes.append((checkbox, option))
            return layout
        else:
            return Label(text='Unsupported question type')
    
    def get_response(self):
        """Get the current response value"""
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
        if self.question_type == 'text':
            self.response_widget.text = ''
        elif self.question_type == 'number':
            self.response_widget.text = ''
        elif self.question_type == 'select':
            self.response_widget.text = 'Select an option'
        elif self.question_type == 'multiselect':
            for checkbox, _ in self.checkboxes:
                checkbox.active = False 