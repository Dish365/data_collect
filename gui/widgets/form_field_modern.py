from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, NumericProperty, BooleanProperty
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.label import MDLabel
from kivymd.uix.label import MDIcon
from kivymd.uix.button import MDIconButton
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.slider import MDSlider
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.clock import Clock
from utils.cross_platform_toast import toast
import datetime
import uuid
import json

# Load the modern KV file
# KV file loaded by main app after theme initialization

class ModernFormField(MDCard):
    """Unified modern form field for all question types"""
    
    # Core properties
    question_text = StringProperty("")
    response_type = StringProperty("text_short")
    question_number = StringProperty("1")
    options = ListProperty([])
    is_required = BooleanProperty(True)
    
    # Advanced properties
    min_value = NumericProperty(1)
    max_value = NumericProperty(5)
    allow_multiple = BooleanProperty(False)
    
    # UI state
    is_expanded = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set up card appearance with responsive sizing
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = self._get_base_height()
        self.elevation = 2
        self.md_bg_color = self._get_card_color()
        self.radius = [16, 16, 16, 16]
        self.padding = [dp(12), dp(10)]  # More compact padding
        self.spacing = dp(6)  # Tighter spacing for better fit
        
        # Initialize components
        Clock.schedule_once(self._setup_ui, 0)
        
        # Bind property changes
        self.bind(response_type=self._on_response_type_change)
        self.bind(options=self._on_options_change)
        self.bind(question_text=self._on_question_text_change)
    
    def _get_base_height(self):
        """Get responsive base height based on response type, expansion state, and content"""
        # Calculate dynamic height based on question text length - more conservative
        question_text_length = len(self.question_text) if self.question_text else 0
        
        # Conservative text height calculation (every 60 characters adds 16dp)
        text_height_bonus = max(0, (question_text_length - 60) // 60) * dp(16)
        
        # Base component heights:
        # Header: 48dp, Question Input: 48dp (base), Content: variable, Actions: 40dp, Padding: 32dp
        header_height = dp(48)
        question_input_base = dp(48)
        actions_height = dp(40)
        padding_spacing = dp(40)  # Total padding and spacing
        
        # Content area heights based on type and state
        content_heights = {
            'text_short': dp(50),
            'text_long': dp(50),
            'choice_single': dp(60) if not self.is_expanded else dp(200),
            'choice_multiple': dp(60) if not self.is_expanded else dp(220),
            'scale_rating': dp(100),
            'date': dp(50),
            'datetime': dp(50),
            'numeric_integer': dp(50),
            'numeric_decimal': dp(50),
            'image': dp(50),
            'audio': dp(50),
            'video': dp(50),
            'file': dp(50),
            'signature': dp(50),
            'barcode': dp(50),
            'geopoint': dp(50),
            'geoshape': dp(50)
        }
        
        content_height = content_heights.get(self.response_type, dp(50))
        
        # Calculate total height
        total_height = header_height + question_input_base + content_height + actions_height + padding_spacing + text_height_bonus
        
        # Ensure minimum height
        return max(total_height, dp(200))
    
    def _get_content_area_height(self):
        """Get content area height based on response type, state, and content"""
        if self.response_type in ['choice_single', 'choice_multiple']:
            if self.is_expanded:
                # Calculate height based on number of options - with proper spacing and padding
                option_count = len(self.options) if self.options else 2
                # Account for padding and spacing in scroll calculation
                option_height_with_spacing = dp(33)  # 30dp option + 3dp spacing
                max_visible_options = 4
                scroll_height = min(option_height_with_spacing * option_count + dp(6), 
                                  option_height_with_spacing * max_visible_options)
                # Layout: label (16dp) + scroll area + spacer (4dp) + buttons (32dp) + spacing (8dp)  
                return dp(16) + scroll_height + dp(4) + dp(32) + dp(8)
            else:
                # Compact preview height
                return dp(50)
        elif self.response_type == 'scale_rating':
            return dp(100)  # Reduced to fit better in card
        else:
            return dp(50)  # Standard content height for simple types
    
    def _get_card_color(self):
        """Get adaptive card color based on theme with KivyMD 2.0.1 compatibility"""
        try:
            from kivy.app import App
            app = App.get_running_app()
            if hasattr(app, 'theme_cls'):
                # Try new KivyMD 2.0.1 properties first
                if hasattr(app.theme_cls, 'surfaceContainerColor'):
                    return app.theme_cls.surfaceContainerColor
                elif hasattr(app.theme_cls, 'surfaceColor'):
                    return app.theme_cls.surfaceColor
                else:
                    # Fallback for older versions
                    return app.theme_cls.bg_normal
        except Exception as e:
            print(f"Theme color error: {e}")
        return (0.98, 0.98, 0.98, 1)  # Light gray fallback
    
    def _setup_ui(self, dt):
        """Set up the UI components with dynamic sizing"""
        self.clear_widgets()
        
        # Update card height based on content first
        self.height = self._get_base_height()
        
        # Header with question number and type
        header = self._create_header()
        self.add_widget(header)
        
        # Question input field (recreate to get proper height)
        self.question_input = self._create_question_input()
        self.add_widget(self.question_input)
        
        # Response-specific content area with adaptive height and tighter spacing
        self.content_area = MDBoxLayout(
            orientation='vertical',
            spacing=dp(4),  # Tighter spacing for better card fit
            size_hint_y=None,
            height=self._get_content_area_height()
        )
        self.add_widget(self.content_area)
        
        # Update content based on response type
        self._update_content()
        
        # Action buttons
        actions = self._create_actions()
        self.add_widget(actions)
    
    def _create_header(self):
        """Create the header with question info and delete button"""
        header = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(12),  # Reduced spacing for better fit
            size_hint_y=None,
            height=dp(48)  # Increased height to accommodate content properly
        )
        
        # Question icon - smaller for better fit
        icon = MDIcon(
            icon=self._get_response_type_icon(),
            size_hint=(None, None),
            size=(dp(20), dp(20)),  # Reduced size
            theme_icon_color="Primary"
        )
        header.add_widget(icon)
        
        # Question number and type - constrained for better fit
        info_layout = MDBoxLayout(
            orientation='vertical', 
            size_hint_x=1,
            spacing=dp(2)  # Reduced spacing between labels
        )
        
        question_label = MDLabel(
            text=f"Question {self.question_number}",
            font_style="Title",
            role="medium",  # Reduced from large
            theme_text_color="Primary",
            bold=True,
            size_hint_y=None,
            height=dp(20)  # Reduced height
        )
        info_layout.add_widget(question_label)
        
        type_label = MDLabel(
            text=self._get_response_type_display(),
            font_style="Label",
            role="small",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(16)
        )
        info_layout.add_widget(type_label)
        
        header.add_widget(info_layout)
        
        # Delete button - smaller for better fit
        delete_btn = MDIconButton(
            icon="delete",
            size_hint=(None, None),
            size=(dp(32), dp(32)),  # Reduced size
            theme_icon_color="Custom",
            icon_color=(0.9, 0.2, 0.2, 1),
            on_release=self._delete_question
        )
        header.add_widget(delete_btn)
        
        return header
    
    def _create_question_input(self):
        """Create the question text input field with proper text wrapping"""
        # Calculate height based on text length - more conservative for card fit
        text_length = len(self.question_text) if self.question_text else 0
        # Multi-line for text over 60 characters (more conservative)
        is_multiline = text_length > 60
        
        # Conservative height calculation
        if is_multiline:
            # For multiline, allow more height but cap it
            estimated_lines = max(1, min(3, (text_length // 60) + 1))  # Max 3 lines
            field_height = dp(48 + ((estimated_lines - 1) * 20))  # 48dp base + 20dp per extra line
        else:
            field_height = dp(48)  # Standard single line height
        
        return MDTextField(
            hint_text=f"Enter your {self._get_response_type_display().lower()} question here...",
            text=self.question_text,
            mode="outlined",
            size_hint_y=None,
            height=field_height,
            multiline=is_multiline,
            on_text=self._on_question_input_change
        )
    
    def _create_actions(self):
        """Create action buttons based on response type"""
        actions = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(6),  # Reduced spacing for better fit
            size_hint_y=None,
            height=dp(40)  # Increased height to match header
        )
        
        # Expand/collapse button for complex types - more compact
        if self.response_type in ['choice_single', 'choice_multiple', 'scale_rating']:
            expand_btn = MDButton(
                style="outlined",
                size_hint=(None, None),
                size=(dp(90), dp(32)),  # Reduced size
                on_release=self._toggle_expanded
            )
            expand_btn.add_widget(MDButtonIcon(icon="chevron-down" if not self.is_expanded else "chevron-up"))
            expand_btn.add_widget(MDButtonText(text="Options" if not self.is_expanded else "Collapse", font_size="11sp"))
            actions.add_widget(expand_btn)
        
        # Add spacer
        actions.add_widget(BoxLayout(size_hint_x=1))
        
        # Required toggle - more compact
        required_btn = MDButton(
            style="filled" if self.is_required else "outlined",
            md_bg_color=(0.2, 0.6, 1.0, 1) if self.is_required else None,
            size_hint=(None, None),
            size=(dp(72), dp(32)),  # Reduced size
            on_release=self._toggle_required
        )
        required_btn.add_widget(MDButtonIcon(icon="asterisk"))
        required_btn.add_widget(MDButtonText(text="Required", font_size="10sp"))  # Smaller font
        actions.add_widget(required_btn)
        
        return actions
    
    def _update_content(self):
        """Update the content area based on response type"""
        self.content_area.clear_widgets()
        
        # Update content area height
        self.content_area.height = self._get_content_area_height()
        
        if self.response_type in ['text_short', 'text_long']:
            self._create_text_preview()
        elif self.response_type in ['numeric_integer', 'numeric_decimal']:
            self._create_numeric_preview()
        elif self.response_type in ['choice_single', 'choice_multiple']:
            self._create_choice_content()
        elif self.response_type == 'scale_rating':
            self._create_rating_content()
        elif self.response_type in ['date', 'datetime']:
            self._create_date_preview()
        elif self.response_type in ['geopoint', 'geoshape']:
            self._create_location_preview()
        elif self.response_type in ['image', 'audio', 'video', 'file']:
            self._create_media_preview()
        elif self.response_type in ['signature', 'barcode']:
            self._create_special_preview()
    
    def _create_text_preview(self):
        """Create preview for text fields"""
        preview = MDTextField(
            hint_text="Answer preview" if self.response_type == 'text_short' else "Detailed answer preview",
            mode="outlined",
            multiline=self.response_type == 'text_long',
            size_hint_y=None,
            height=dp(48) if self.response_type == 'text_short' else dp(80),
            disabled=True
        )
        self.content_area.add_widget(preview)
    
    def _create_numeric_preview(self):
        """Create preview for numeric fields"""
        preview = MDTextField(
            hint_text="123" if self.response_type == 'numeric_integer' else "123.45",
            mode="outlined",
            input_filter="int" if self.response_type == 'numeric_integer' else "float",
            size_hint_y=None,
            height=dp(48),
            disabled=True
        )
        self.content_area.add_widget(preview)
    
    def _create_choice_content(self):
        """Create content for choice fields with compact spacing"""
        # Options label - very compact
        label = MDLabel(
            text=f"Options ({len(self.options)}):",
            font_style="Body",
            role="small",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(16)  # Very compact height
        )
        self.content_area.add_widget(label)
        
        # Options preview or editor
        if self.is_expanded:
            self._create_options_editor()
        else:
            self._create_options_preview()
    
    def _create_options_preview(self):
        """Create a preview of options with proper text wrapping"""
        if not self.options:
            preview_text = "No options set"
        else:
            # Truncate long options for preview
            truncated_options = []
            for opt in self.options[:3]:
                if len(str(opt)) > 25:
                    truncated_options.append(str(opt)[:22] + "...")
                else:
                    truncated_options.append(str(opt))
            
            preview_text = ", ".join(truncated_options)
            if len(self.options) > 3:
                preview_text += f" (+{len(self.options) - 3} more)"
        
        # Very compact height calculation
        text_height = dp(20) if len(preview_text) > 50 else dp(16)
        
        preview = MDLabel(
            text=preview_text,
            font_style="Body",
            role="small",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=text_height,
            text_size=(None, None),  # Enable text wrapping
            halign="left"
        )
        self.content_area.add_widget(preview)
    
    def _create_options_editor(self):
        """Create the options editor with proper height management"""
        from kivymd.uix.scrollview import MDScrollView
        
        # Ensure minimum 2 options before creating editor
        while len(self.options) < 2:
            self.options.append(f"Option {len(self.options) + 1}")
        
        # Better height calculation - account for padding and spacing
        option_height_with_spacing = dp(33)  # 30dp option + 3dp spacing
        max_visible_options = 4
        options_height = min(option_height_with_spacing * len(self.options) + dp(6), 
                           option_height_with_spacing * max_visible_options)  # Include padding in calculation
        
        # Options container with scroll - better positioning
        scroll = MDScrollView(
            size_hint_y=None,
            height=options_height,
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(3),  # Slightly thicker for better visibility
            scroll_type=['bars']  # Ensure scroll bars are visible
        )
        
        options_container = MDBoxLayout(
            id='options_container',
            orientation='vertical',
            spacing=dp(3),  # Better spacing between options
            size_hint_y=None,
            height=dp(33) * len(self.options) + dp(6),  # Account for 30dp layout + 3dp spacing per option
            padding=[dp(2), dp(4), dp(2), dp(4)]  # Proper padding to prevent cutoff at top/bottom
        )
        
        # Add existing options
        for i, option in enumerate(self.options):
            option_widget = self._create_option_widget(i, option)
            options_container.add_widget(option_widget)
        
        scroll.add_widget(options_container)
        self.content_area.add_widget(scroll)
        
        # Ensure scroll starts at top to show first option properly
        Clock.schedule_once(lambda dt: setattr(scroll, 'scroll_y', 1), 0.1)
        
        # Add spacing between scroll and buttons
        spacer = MDBoxLayout(
            size_hint_y=None,
            height=dp(4)  # Small spacer to separate scroll from buttons
        )
        self.content_area.add_widget(spacer)
        
        # Add/Remove buttons with proper spacing
        btn_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(6),  # Better spacing
            size_hint_y=None,
            height=dp(32),  # Better height
            padding=[0, dp(2), 0, 0]
        )
        
        add_btn = MDButton(
            style="filled",
            md_bg_color=(0.27, 0.65, 0.27, 1),
            size_hint=(None, None),
            size=(dp(76), dp(28)),  # Better size
            on_release=self._add_option
        )
        add_btn.add_widget(MDButtonIcon(icon="plus"))
        add_btn.add_widget(MDButtonText(text="Add", font_size="11sp"))  # Better font size
        btn_layout.add_widget(add_btn)
        
        remove_btn = MDButton(
            style="outlined",
            size_hint=(None, None),
            size=(dp(88), dp(28)),  # Better size
            on_release=self._remove_option,
            disabled=len(self.options) <= 2
        )
        remove_btn.add_widget(MDButtonIcon(icon="minus"))
        remove_btn.add_widget(MDButtonText(text="Remove", font_size="11sp"))  # Better font size
        btn_layout.add_widget(remove_btn)
        
        btn_layout.add_widget(BoxLayout(size_hint_x=1))  # Spacer
        
        self.content_area.add_widget(btn_layout)
    
    def _create_option_widget(self, index, text):
        """Create a single option input widget with proper layout"""
        option_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(6),  # Better spacing for readability
            size_hint_y=None,
            height=dp(30),  # Fixed height
            padding=[dp(2), 0, dp(2), 0]  # Small horizontal padding
        )
        
        # Option number label - properly sized
        number_label = MDLabel(
            text=f"{index + 1}.",
            size_hint=(None, None),
            size=(dp(18), dp(30)),  # Slightly wider for better alignment
            font_style="Body",
            role="small",
            theme_text_color="Primary",
            valign="center",
            halign="center"
        )
        option_layout.add_widget(number_label)
        
        # Option input field - properly contained
        option_input = MDTextField(
            text=text,
            hint_text=f"Option {index + 1}",
            mode="outlined",
            size_hint_x=1,
            size_hint_y=None,
            height=dp(32),  # Slightly taller for better visibility
            on_text=lambda instance, value: self._update_option(index, value)
        )
        option_layout.add_widget(option_input)
        
        return option_layout
    
    def _create_rating_content(self):
        """Create content for rating scale"""
        # Scale preview - more compact
        scale_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(4),  # Reduced spacing
            size_hint_y=None,
            height=dp(68)  # Reduced height
        )
        
        label = MDLabel(
            text=f"Rating Scale ({self.min_value}-{self.max_value}):",
            font_style="Body",
            role="small",  # Smaller role
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(18)  # Reduced height
        )
        scale_layout.add_widget(label)
        
        slider = MDSlider(
            min=self.min_value,
            max=self.max_value,
            value=(self.min_value + self.max_value) / 2,
            step=1,
            disabled=True,
            size_hint_y=None,
            height=dp(28)  # Reduced height
        )
        scale_layout.add_widget(slider)
        
        # Min/Max labels - more compact
        labels_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(18)  # Reduced height
        )
        
        min_label = MDLabel(
            text=f"{self.min_value} (Poor)",
            font_style="Label",
            role="small",
            theme_text_color="Secondary",
            halign="left"
        )
        labels_layout.add_widget(min_label)
        
        labels_layout.add_widget(BoxLayout(size_hint_x=1))  # Spacer
        
        max_label = MDLabel(
            text=f"{self.max_value} (Excellent)",
            font_style="Label",
            role="small",
            theme_text_color="Secondary",
            halign="right"
        )
        labels_layout.add_widget(max_label)
        
        scale_layout.add_widget(labels_layout)
        self.content_area.add_widget(scale_layout)
    
    def _create_date_preview(self):
        """Create preview for date fields"""
        if self.response_type == 'date':
            preview = MDButton(
                style="outlined",
                size_hint_y=None,
                height=dp(48),
                disabled=True
            )
            preview.add_widget(MDButtonIcon(icon="calendar"))
            preview.add_widget(MDButtonText(text="Select Date", font_size="14sp"))
        else:  # datetime
            preview = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(8),
                size_hint_y=None,
                height=dp(48)
            )
            
            date_btn = MDButton(style="outlined", size_hint_x=1, height=dp(48), disabled=True)
            date_btn.add_widget(MDButtonIcon(icon="calendar"))
            date_btn.add_widget(MDButtonText(text="Date", font_size="14sp"))
            preview.add_widget(date_btn)
            
            time_btn = MDButton(style="outlined", size_hint_x=1, height=dp(48), disabled=True)
            time_btn.add_widget(MDButtonIcon(icon="clock-outline"))
            time_btn.add_widget(MDButtonText(text="Time", font_size="14sp"))
            preview.add_widget(time_btn)
        
        self.content_area.add_widget(preview)
    
    def _create_location_preview(self):
        """Create preview for location fields"""
        preview = MDButton(
            style="outlined",
            size_hint_y=None,
            height=dp(48),
            disabled=True
        )
        preview.add_widget(MDButtonIcon(icon="map-marker" if self.response_type == 'geopoint' else "vector-polygon"))
        preview.add_widget(MDButtonText(text="Get Location" if self.response_type == 'geopoint' else "Capture Area", font_size="14sp"))
        self.content_area.add_widget(preview)
    
    def _create_media_preview(self):
        """Create preview for media fields"""
        icon_map = {
            'image': 'camera',
            'audio': 'microphone',
            'video': 'video',
            'file': 'file'
        }
        
        text_map = {
            'image': 'Take Photo',
            'audio': 'Record Audio',
            'video': 'Record Video',
            'file': 'Upload File'
        }
        
        preview = MDButton(
            style="outlined",
            size_hint_y=None,
            height=dp(48),
            disabled=True
        )
        preview.add_widget(MDButtonIcon(icon=icon_map.get(self.response_type, 'file')))
        preview.add_widget(MDButtonText(text=text_map.get(self.response_type, 'Upload'), font_size="14sp"))
        self.content_area.add_widget(preview)
    
    def _create_special_preview(self):
        """Create preview for special fields"""
        icon_map = {
            'signature': 'signature',
            'barcode': 'qrcode'
        }
        
        text_map = {
            'signature': 'Capture Signature',
            'barcode': 'Scan Barcode'
        }
        
        preview = MDButton(
            style="outlined",
            size_hint_y=None,
            height=dp(48),
            disabled=True
        )
        preview.add_widget(MDButtonIcon(icon=icon_map.get(self.response_type, 'help')))
        preview.add_widget(MDButtonText(text=text_map.get(self.response_type, 'Action'), font_size="14sp"))
        self.content_area.add_widget(preview)
    
    # Event handlers
    def _on_response_type_change(self, instance, value):
        """Handle response type changes with animation"""
        if hasattr(self, 'content_area'):
            # Update height responsively
            new_height = self._get_base_height()
            self.height = new_height
            self._update_content()
    
    def _animate_height_change(self, new_height):
        """Animate height change for smooth transitions"""
        from kivy.animation import Animation
        anim = Animation(height=new_height, duration=0.3, t='out_cubic')
        anim.start(self)
    
    def _on_options_change(self, instance, value):
        """Handle options changes"""
        if hasattr(self, 'content_area') and self.response_type in ['choice_single', 'choice_multiple']:
            if self.is_expanded:
                self._update_content()
    
    def _on_question_text_change(self, instance, value):
        """Handle question text changes"""
        if hasattr(self, 'question_input'):
            self.question_input.text = value
    
    def _on_question_input_change(self, instance, value):
        """Handle question input field changes"""
        self.question_text = value
    
    def _delete_question(self, instance):
        """Delete this question with confirmation"""
        question_preview = self.get_question_text() or f"{self._get_response_type_display()} question"
        if len(question_preview) > 30:
            question_preview = question_preview[:27] + "..."
        
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDButton, MDButtonText
        
        def confirm_delete(dialog_instance):
            if self.parent:
                self.parent.remove_widget(self)
            toast(f"✓ Deleted question", duration=2)
            dialog_instance.dismiss()
        
        def cancel_delete(dialog_instance):
            dialog_instance.dismiss()
        
        # Create confirmation dialog
        dialog = MDDialog(
            title="Delete Question?",
            text=f'Are you sure you want to delete "{question_preview}"?',
            auto_dismiss=False
        )
        
        # Add buttons
        cancel_btn = MDButton(
            style="text",
            on_release=lambda x: cancel_delete(dialog)
        )
        cancel_btn.add_widget(MDButtonText(text="Cancel"))
        
        delete_btn = MDButton(
            style="text",
            theme_bg_color="Custom",
            md_bg_color=(0.9, 0.2, 0.2, 1),
            on_release=lambda x: confirm_delete(dialog)
        )
        delete_btn.add_widget(MDButtonText(text="Delete", text_color=(1, 1, 1, 1)))
        
        dialog.buttons = [cancel_btn, delete_btn]
        dialog.open()
    
    def _toggle_expanded(self, instance):
        """Toggle expanded state for complex types"""
        self.is_expanded = not self.is_expanded
        
        # Update heights with animation
        new_height = self._get_base_height()
        self._animate_height_change(new_height)
        
        # Schedule content update after animation starts
        Clock.schedule_once(lambda dt: self._update_content(), 0.05)
        
        # Update button text and icon
        if hasattr(instance, 'children'):
            for child in instance.children:
                if isinstance(child, MDButtonText):
                    child.text = "Collapse" if self.is_expanded else "Options"
                elif isinstance(child, MDButtonIcon):
                    child.icon = "chevron-up" if self.is_expanded else "chevron-down"
    
    def _toggle_required(self, instance):
        """Toggle required state"""
        self.is_required = not self.is_required
        
        # Update button appearance
        if self.is_required:
            instance.style = "filled"
            instance.md_bg_color = (0.2, 0.6, 1.0, 1)
        else:
            instance.style = "outlined"
            instance.md_bg_color = None
        
        status = "required" if self.is_required else "optional"
        toast(f"✓ Question is now {status}", duration=1.5)
    
    def _add_option(self, instance):
        """Add a new option and refresh editor"""
        new_option = f"Option {len(self.options) + 1}"
        self.options = self.options + [new_option]
        
        # Refresh the options editor if expanded
        if self.is_expanded:
            Clock.schedule_once(lambda dt: self._update_content(), 0.1)
        
        toast(f"✓ Added option {len(self.options)}", duration=1.5)
    
    def _remove_option(self, instance):
        """Remove the last option and refresh editor"""
        if len(self.options) > 2:
            removed_count = len(self.options)
            self.options = self.options[:-1]
            
            # Refresh the options editor if expanded
            if self.is_expanded:
                Clock.schedule_once(lambda dt: self._update_content(), 0.1)
            
            toast(f"✓ Removed option {removed_count}", duration=1.5)
        else:
            toast("⚠ Choice questions need at least 2 options", duration=2)
    
    def _update_option(self, index, value):
        """Update a specific option"""
        if 0 <= index < len(self.options):
            new_options = list(self.options)
            new_options[index] = value
            self.options = new_options
    
    # Utility methods
    def _get_response_type_icon(self):
        """Get icon for response type"""
        icon_map = {
            'text_short': 'text-short',
            'text_long': 'text-long',
            'numeric_integer': 'numeric',
            'numeric_decimal': 'numeric-9-plus',
            'choice_single': 'radiobox-marked',
            'choice_multiple': 'checkbox-marked',
            'scale_rating': 'star',
            'date': 'calendar',
            'datetime': 'calendar-clock',
            'geopoint': 'map-marker',
            'geoshape': 'vector-polygon',
            'image': 'camera',
            'audio': 'microphone',
            'video': 'video',
            'file': 'file',
            'signature': 'signature',
            'barcode': 'qrcode'
        }
        return icon_map.get(self.response_type, 'help-circle')
    
    def _get_response_type_display(self):
        """Get display name for response type"""
        display_map = {
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
            'geoshape': 'GPS Area',
            'image': 'Photo/Image',
            'audio': 'Audio Recording',
            'video': 'Video Recording',
            'file': 'File Upload',
            'signature': 'Digital Signature',
            'barcode': 'Barcode/QR Code'
        }
        return display_map.get(self.response_type, self.response_type.replace('_', ' ').title())
    
    # Data methods
    def get_question_text(self):
        """Get the current question text"""
        return self.question_text.strip()
    
    def get_value(self):
        """Get the current field value (for preview/testing)"""
        return ""
    
    def validate(self):
        """Validate the field configuration"""
        errors = []
        
        # Validate question text
        if not self.get_question_text():
            errors.append("Question text is required")
        elif len(self.get_question_text()) < 3:
            errors.append("Question text must be at least 3 characters long")
        
        # Validate choice options
        if self.response_type in ['choice_single', 'choice_multiple']:
            valid_options = [opt.strip() for opt in self.options if opt.strip()]
            if len(valid_options) < 2:
                errors.append("Choice questions need at least 2 options")
        
        # Validate rating scale
        if self.response_type == 'scale_rating':
            if self.min_value >= self.max_value:
                errors.append("Maximum value must be greater than minimum value")
        
        return len(errors) == 0, errors
    
    def to_dict(self):
        """Convert field to dictionary for saving"""
        return {
            'question_text': self.get_question_text(),
            'response_type': self.response_type,
            'options': [opt.strip() for opt in self.options if opt.strip()] if self.response_type in ['choice_single', 'choice_multiple'] else [],
            'allow_multiple': self.response_type == 'choice_multiple',
            'is_required': self.is_required,
            'validation_rules': {
                'min_value': self.min_value,
                'max_value': self.max_value
            } if self.response_type == 'scale_rating' else {}
        }


def create_form_field(response_type, question_text="", options=None, **kwargs):
    """Factory function to create modern form fields"""
    field = ModernFormField(
        response_type=response_type,
        question_text=question_text,
        options=options or [],
        **kwargs
    )
    return field