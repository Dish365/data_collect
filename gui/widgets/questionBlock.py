from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, BooleanProperty
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.core.window import Window

# Load the KV file
Builder.load_file("kv/question_block.kv")


class QuestionBlock(MDCard):
    """Modern question block widget using KivyMD 2.0.1 Material Design"""
    
    question_text = StringProperty("")
    answer_type = StringProperty("Short Answer")
    allow_multiple = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Setup responsive properties
        self.update_responsive_properties()
        
        # Bind to window resize for responsive updates
        Window.bind(on_resize=self._on_window_resize)
        
        # Initialize options widgets list
        self.options_widgets = []
        
        # Bind properties
        self.bind(question_text=self._update_question_text)
        self.bind(answer_type=self._update_answer_type)
        self.bind(allow_multiple=self._update_allow_multiple)
    
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
                self.padding = [dp(20), dp(16)]
                self.spacing = dp(16)
            elif category == "tablet":
                self.padding = [dp(16), dp(12)]
                self.spacing = dp(14)
            elif category == "small_tablet":
                self.padding = [dp(14), dp(10)]
                self.spacing = dp(12)
            else:  # phone
                self.padding = [dp(12), dp(8)]
                self.spacing = dp(10)
                
        except Exception as e:
            print(f"Error updating QuestionBlock responsive properties: {e}")
            # Fallback to default values
            self.padding = [dp(12), dp(8)]
            self.spacing = dp(10)
    
    def _update_question_text(self, instance, value):
        """Update question text in UI"""
        if hasattr(self, 'question_input'):
            self.question_input.text = value
    
    def _update_answer_type(self, instance, value):
        """Update answer type and recreate answer area"""
        if hasattr(self, 'type_button'):
            self.type_button.text = value
        self._update_answer_area()
    
    def _update_allow_multiple(self, instance, value):
        """Update allow multiple setting"""
        if hasattr(self, 'toggle_switch'):
            self.toggle_switch.active = value
    
    def _update_answer_area(self):
        """Update the answer area based on answer type"""
        if not hasattr(self, 'answer_area'):
            return
            
        # Clear existing widgets
        self.answer_area.clear_widgets()
        
        # Create appropriate widget based on answer type using KV
        from kivy.lang import Builder
        
        if self.answer_type == "Short Answer":
            widget = Builder.load_string('''
ShortAnswerPreview:
''')
            self.answer_area.add_widget(widget)
            
        elif self.answer_type == "Long Answer":
            widget = Builder.load_string('''
LongAnswerPreview:
''')
            self.answer_area.add_widget(widget)
            
        elif self.answer_type == "Multiple Choice":
            widget = Builder.load_string('''
MultipleChoicePreview:
''')
            self.answer_area.add_widget(widget)
            # Store reference for option management
            self.multiple_choice_widget = widget
    
    def get_multiple_choice_widget(self):
        """Get reference to multiple choice widget for option management"""
        return getattr(self, 'multiple_choice_widget', None)
    
    def _on_toggle_multiple(self, instance, value):
        """Handle toggle switch change"""
        self.allow_multiple = value
    
    def add_option(self, *args):
        """Add a new option to multiple choice widget"""
        widget = self.get_multiple_choice_widget()
        if widget and hasattr(widget, 'add_option'):
            widget.add_option()
    
    def remove_option(self, widget):
        """Remove an option from multiple choice widget"""
        mc_widget = self.get_multiple_choice_widget()
        if mc_widget and hasattr(mc_widget, 'remove_option'):
            mc_widget.remove_option(widget)
    
    def open_menu(self, instance):
        """Open the answer type dropdown menu"""
        if hasattr(self, 'menu'):
            self.menu.caller = instance
            self.menu.open()
    
    def set_answer_type(self, answer_type):
        """Set the answer type"""
        self.answer_type = answer_type
    
    def to_dict(self):
        """Convert question block to dictionary"""
        return {
            "question": self.question_text,
            "type": self.answer_type,
            "options": [w.text.strip() for w in self.options_widgets] if self.answer_type == "Multiple Choice" else [],
            "allow_multiple": self.allow_multiple
        }
    
    def render_preview(self):
        """Render a preview of the question"""
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.selectioncontrol import MDCheckbox
        from kivymd.uix.label import MDLabel
        from kivymd.uix.textfield import MDTextField
        
        preview = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8)
        )
        
        preview.add_widget(MDLabel(
            text=self.question_text,
            font_style="Subtitle1"
        ))
        
        if self.answer_type == "Short Answer":
            preview.add_widget(MDTextField(
                hint_text="Short answer",
                mode="rectangle"
            ))
            
        elif self.answer_type == "Long Answer":
            preview.add_widget(MDTextField(
                hint_text="Long answer",
                multiline=True,
                mode="rectangle"
            ))
            
        elif self.answer_type == "Multiple Choice":
            for opt in self.options_widgets:
                row = MDBoxLayout(
                    orientation="horizontal",
                    spacing=dp(8),
                    size_hint_y=None,
                    height=dp(40)
                )
                row.add_widget(MDCheckbox(
                    size_hint=(None, None),
                    size=(dp(36), dp(36))
                ))
                row.add_widget(MDLabel(text=opt.text))
                preview.add_widget(row)
        
        return preview
